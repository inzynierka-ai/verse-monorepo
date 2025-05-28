from typing import List, Optional, cast, Union
import logging
import json

from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.models.character import Character
from app.services.platform.llm import LLMService, ModelName
from langfuse.decorators import observe  # type: ignore

from app.crud.characters import get_character
from app.schemas.message import Message  # type: ignore
from app.utils.json_service import JSONService


class RelationshipAnalysisResponse(BaseModel):
    _thinking: str
    relationshipLevel: int = Field(..., ge=0, le=100)


class RelationshipAnalysisError(BaseModel):
    error: str


class RelationshipAnalysisResult(BaseModel):
    character_id: int
    character_name: str
    previous_level: int
    new_level: int
    relationship_tier: str
    analysis: str
    change: int


class RelationshipAnalysisService:
    """
    Service for analyzing relationship between player and character based on conversation.
    """

    def __init__(self, db: Session, llm_service: Optional[LLMService] = None):
        self.db = db
        self.llm_service = llm_service or LLMService()
        self.logger = logging.getLogger(__name__)

        # Relationship level ranges
        self.relationship_tiers = {
            "stranger_or_enemy": (0, 20),
            "acquaintance": (21, 40),
            "friend": (41, 60),
            "close_friend": (61, 80),
            "family": (81, 100)
        }

    @observe(name="analyze_relationship")  # type: ignore
    async def analyze_relationship(self, character_id: int, messages: List[Message], update_db: bool = True) -> Union[RelationshipAnalysisResult, RelationshipAnalysisError]:
        """
        Analyzes a conversation's impact on relationship between player and character.

        Args:
            character_id: ID of the character to analyze relationship with
            messages: List of message objects from the conversation
            update_db: Whether to update the relationship level in the database

        Returns:
            RelationshipAnalysisResult or RelationshipAnalysisError
        """
        if not messages:
            return RelationshipAnalysisError(error="No messages provided for analysis")

        # Get current character data
        character = get_character(self.db, character_id)
        if not character:
            return RelationshipAnalysisError(error=f"Character with ID {character_id} not found")

        # Use a default value of 50 if relationship_level is None
        current_level: int = 50  # Default to neutral
        db_level = getattr(character, "relationship_level", None)
        if db_level is not None:
            current_level = cast(int, db_level)

        # Format messages for analysis
        formatted_messages = self._format_messages_for_analysis(messages)

        # Generate analysis using LLM
        try:
            analysis = await self._generate_relationship_analysis(
                character=character,
                current_level=current_level,
                formatted_messages=formatted_messages
            )

            # Extract new relationship level from analysis
            new_level = self._extract_relationship_level(analysis, current_level)

            # Get relationship tier (textual description)
            tier = self._get_relationship_tier(new_level)

            # Prepare result
            result = RelationshipAnalysisResult(
                character_id=character_id,
                character_name=str(character.name),
                previous_level=current_level,
                new_level=new_level,
                relationship_tier=tier,
                analysis=analysis,
                change=new_level - current_level
            )

            # Update database if requested
            if update_db:
                setattr(character, "relationship_level", new_level)
                self.db.commit()

            return result

        except Exception as e:
            self.logger.error(f"Error analyzing relationship: {str(e)}")
            return RelationshipAnalysisError(error=f"Error analyzing relationship: {str(e)}")

    def _format_messages_for_analysis(self, messages: List[Message]) -> str:
        """Format messages into a string for LLM analysis."""
        formatted_messages: List[str] = []

        for msg in messages:
            speaker = "Player"
            if msg.role == "assistant":
                # Safely handle character name access
                try:
                    if hasattr(msg, "character"):
                        char = getattr(msg, "character", None)
                        if char and hasattr(char, "name"):
                            speaker = str(getattr(char, "name", "Character"))
                except Exception:
                    # Fallback if any attribute access fails
                    speaker = "Character"
            elif msg.role == "system":
                speaker = "System"

            formatted_messages.append(f"{speaker}: {msg.content}")

        return "\n".join(formatted_messages)

    @observe(name="generate_relationship_analysis")
    async def _generate_relationship_analysis(
        self,
        character: Character,
        current_level: int,
        formatted_messages: str
    ) -> str:
        """Generate relationship analysis using LLM."""

        # Safely access attributes
        personality = "Not specified"
        try:
            personality_traits = getattr(character, "personality_traits", None)
            if personality_traits:
                personality = str(personality_traits)
        except Exception:
            pass

        goals = "Not specified"
        try:
            char_goals = getattr(character, "goals", None)
            if char_goals:
                goals = str(char_goals)
        except Exception:
            pass

        system_prompt = f"""
        You are a relationship analyst for a narrative game. You need to analyze how the conversation 
        affects the relationship between the player and the character '{character.name}'.
        
        Character information:
        - Name: {character.name}
        - Role: {character.role}
        - Description: {character.brief_description}
        - Personality: {personality}
        - Goals: {goals}
        
        Current relationship level: {current_level}/100
        
        Relationship levels are defined as:
        - 0-20: Stranger or enemy
        - 21-40: Acquaintance
        - 41-60: Friend
        - 61-80: Close friend
        - 81-100: Family/intimate
        
        Important rules:
        1. Trust builds slowly but can be lost quickly
        2. Meaningful interactions should have more impact than small talk
        3. Actions that align with a character's goals/values strengthen the relationship
        4. Actions that contradict a character's goals/values weaken the relationship
        5. Betrayals or significant negative actions can cause large relationship drops
        
        Analyze how the conversation affects the relationship between the player and {character.name}.
        Be specific about what elements in the conversation influenced your decision.
        
        Provide your response in the following JSON format:
        {{
            "_thinking": "Your detailed analysis explaining how the conversation impacts their relationship. Include specific interactions that strengthened or weakened the relationship.",
            "relationshipLevel": number_between_0_and_100
        }}
        """

        # User message just contains the conversation
        user_prompt = formatted_messages

        messages = [
            self.llm_service.create_message("system", system_prompt),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GPT41_MINI,
            temperature=0.3,
            max_tokens=1500
        )

        # Handle the case where response is an AsyncGenerator
        if hasattr(response, "__aiter__"):
            # If it's a streaming response, extract all content
            content = await self.llm_service.extract_content(response)
            return content
        return str(response)

    def _extract_relationship_level(self, analysis: str, current_level: int) -> int:
        """Extract new relationship level from LLM analysis."""
        try:

            # Parse the response using JSONService and validate with Pydantic model
            response_data = JSONService.parse_and_validate_json_response(
                analysis,
                RelationshipAnalysisResponse
            )

            # Get the new relationship level from the validated response
            new_level = response_data.relationshipLevel

            # Apply rule: trust builds slowly but can be lost quickly
            if new_level > current_level:
                # When improving, limit the increase to smaller increments
                max_improvement = 10  # Maximum points that can be gained in one conversation
                new_level = min(current_level + max_improvement, new_level)

            return new_level

        except (ValueError, json.JSONDecodeError) as e:
            # If validation with Pydantic model fails, try with required keys
            self.logger.warning(f"Failed to validate with Pydantic model: {str(e)}")

        return current_level

    def _get_relationship_tier(self, level: int) -> str:
        """Get the relationship tier based on the level."""
        for tier, (min_val, max_val) in self.relationship_tiers.items():
            if min_val <= level <= max_val:
                return tier

        return "unknown"  # Should never happen with proper bounds checking
