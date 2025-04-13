import logging
import uuid
from typing import Optional
from app.services.llm import LLMService, ModelName
from app.schemas.story_generation import (
    CharacterFromLLM,
    Story,
    Character,
    CharacterDraft
)
from app.prompts import (
    CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE,
    DESCRIBE_CHARACTER_SYSTEM_PROMPT,
    CREATE_CHARACTER_JSON_SYSTEM_PROMPT,
    CREATE_CHARACTER_JSON_USER_PROMPT_TEMPLATE,
    CHARACTER_IMAGE_PROMPT_SYSTEM_PROMPT,
    CHARACTER_IMAGE_PROMPT_USER_TEMPLATE
)
from app.utils.json_service import JSONService
from app.services.image_generation.comfyui_service import ComfyUIService
from app.core.config import settings
from sqlalchemy.orm import Session
from app.models.character import Character as CharacterModel


class CharacterGenerator:
    """
    Service for generating characters.        
    """

    def __init__(self, llm_service: Optional[LLMService] = None, db_session: Optional[Session] = None):
        self.llm_service = llm_service or LLMService()
        self.db_session = db_session

    async def generate_character(self, character_draft: CharacterDraft, story: Story, is_player: bool, story_id: int) -> CharacterModel | None:
        """
        Orchestrates the entire character generation process.

        Args:
            character_draft: Character draft to be used for character generation
            story: Story object containing description and other details
            is_player: Whether this is a player character
            story_id: ID of the story to associate the character with

        Returns:
            Fully generated Character object with description and image prompt
        """
        # 1. Generate detailed character description
        character_description = await self._describe_character(character_draft, story)
        # 2. Create character JSON from description
        character_from_llm = await self._create_character_json(character_description)
        # 3. Generate image prompt for the character
        image_prompt = await self._generate_image_prompt(character_from_llm, story.description)
        # 4. Generate image for the character
        image_url = await self._generate_image(image_prompt)

        # Create Character object from CharacterFromLLM
        character = Character(
            **character_from_llm.model_dump(),
            imageUrl=image_url,
            role="player" if is_player else "npc"
        )
        # Save to database but return the Pydantic model
        self._save_character_to_db(character, story_id, image_prompt, is_player)
        
        # Return the Pydantic Character object
        return character
         
        
    def _save_character_to_db(self, character: Character, story_id: int, image_prompt: str, is_player: bool) -> CharacterModel | None:
        """
        Save the generated character to the database.
        
        Args:
            character: The generated character object
            story_id: ID of the story to associate with
            image_prompt: The image prompt used to generate the character image
            is_player: Whether this is a player character
        """
        try:
            # Safely get character attributes
            personality_traits = ""
            if hasattr(character, 'personalityTraits') and character.personalityTraits is not None:
                personality_traits = ", ".join(character.personalityTraits)
                
            # For relationships, serialize to string if it exists
            relationships_str = ""
            if hasattr(character, 'relationships') and character.relationships:
                # Convert relationships to JSON string
                import json
                try:
                    relationships_str = json.dumps(character.relationships)
                except Exception as e:
                    logging.warning(f"Failed to convert relationships to JSON: {str(e)}")
                    relationships_str = ""
            
            # Create a database model from the character schema
            db_character = CharacterModel(
                name=character.name,
                role="player" if is_player else "npc",
                description=character.description,
                personality_traits=personality_traits,
                backstory=character.backstory,
                goals=", ".join(character.goals) if hasattr(character, 'goals') and character.goals else "",
                speaking_style="", # Not in schema, add if needed
                relationships=relationships_str,
                image_dir=character.imageUrl,  # Default directory
                image_prompt=image_prompt,
                relationship_level=0,  # Default starting level
                story_id=story_id,
                uuid=str(uuid.uuid4())  # Generate a new UUID
            )
            
            # Add to database session if available
            if self.db_session is not None:
                self.db_session.add(db_character)
                self.db_session.commit()
                logging.info(f"Character {character.name} saved to database with ID {db_character.id}")
                return db_character
        except Exception as e:
            logging.exception(f"Failed to save character to database: {str(e)}")
            # Don't raise the exception, just log it, to avoid breaking the game flow
            if self.db_session is not None and hasattr(self.db_session, 'is_active') and self.db_session.is_active:
                self.db_session.rollback()

    async def _describe_character(
        self,
        character: CharacterDraft,
        story: Story
    ) -> str:
        """
        Generate a detailed narrative description of a character based on character draft and story description.

        Args:
            character: Character draft to be used for character generation
            story: Story object containing description and other details

        Returns:
            A detailed narrative description of a single character
        """
        user_prompt = self._create_character_prompt(character, story)

        messages = [
            self.llm_service.create_message("system", DESCRIBE_CHARACTER_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GPT4O_MINI,
            temperature=0.7,
            stream=False
        )

        return await self.llm_service.extract_content(response)

    async def _generate_image(self, image_prompt: str) -> str:
        """
        Generate an image for a character.
        """
        import asyncio
        
        comfyui_service = ComfyUIService()
        logging.info(f"Generating image for prompt: {image_prompt}")
        
        # Run the synchronous generate_image method in a thread pool
        loop = asyncio.get_event_loop()
        result_dict = await loop.run_in_executor(
            None, 
            lambda: comfyui_service.generate_image(image_prompt, "character")
        )
        
        logging.info(f"Generated image: {result_dict}")
        return f"{settings.BACKEND_URL}{result_dict['imagePath']}"

    async def _generate_image_prompt(
        self,
        character: CharacterFromLLM,
        story_description: str
    ) -> str:
        """
        Generate a detailed image prompt for a character.

        Args:
            character: The detailed character to generate an image prompt for
            story_description: The story description for context

        Returns:
            A detailed image prompt for the character
        """
        user_prompt = CHARACTER_IMAGE_PROMPT_USER_TEMPLATE.format(
            character_name=character.name,
            character_description=character.description,
            story_description=story_description
        )

        messages = [
            self.llm_service.create_message("system", CHARACTER_IMAGE_PROMPT_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GPT4O_MINI,
            temperature=0.7,
            stream=False
        )

        return await self.llm_service.extract_content(response)

    async def _create_character_json(
        self,
        character_description: str
    ) -> CharacterFromLLM:
        """
        Generate a detailed character profile based on character description.

        Args:
            character_description: Detailed character description

        Returns:
            Character object containing detailed character profile
        """
        user_prompt = CREATE_CHARACTER_JSON_USER_PROMPT_TEMPLATE.format(
            character_descriptions=character_description
        )

        messages = [
            self.llm_service.create_message("system", CREATE_CHARACTER_JSON_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GPT4O_MINI,
            temperature=0.7,
            stream=False
        )

        response_text = await self.llm_service.extract_content(response)

        try:
            # Parse the JSON response into a character object
            character = JSONService.parse_and_validate_json_response(
                response_text, CharacterFromLLM)

            if not character:
                raise ValueError("No character data found in response")

            return character
        except Exception as e:
            raise ValueError(
                f"Failed to parse character data: {str(e)}, raw response: {response_text}") from e

    def _create_character_prompt(
        self,
        character: CharacterDraft,
        story: Story
    ) -> str:
        """
        Create a formatted prompt for character generation.

        Args:
            character: The character draft to be used for character generation
            story: The story description

        Returns:
            Formatted prompt string
        """
        return CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE.format(
            character_draft=character,
            story_description=story.description,
            story_rules=story.rules
        )
