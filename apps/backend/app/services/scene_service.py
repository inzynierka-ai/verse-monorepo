from sqlalchemy.orm import Session
from typing import Optional, cast, List, Dict
import uuid
from app.models.scene import Scene
from app.crud import scenes
from app.services.llm import LLMService, ModelName
from app.schemas.message import Message as MessageSchema
from app.schemas.scene import Scene as SceneSchema
from app.crud.characters import get_character


class SceneService:
    def __init__(self):
        self.llm_service = LLMService()
        
    def fetch_latest_scene(self, db: Session, story_id: int) -> Optional[Scene]:
        """Fetch the latest scene for a story"""
        return scenes.get_latest_scene_by_story(db, story_id)
    
    def fetch_latest_active_scene(self, db: Session, story_id: int) -> Optional[Scene]:
        """Fetch the latest active scene for a story"""
        return scenes.get_latest_active_scene_by_story(db, story_id)
    
    def fetch_latest_completed_scene(self, db: Session, story_id: int) -> Optional[Scene]:
        """Fetch the latest completed scene for a story"""
        return scenes.get_latest_completed_scene_by_story(db, story_id)
    
    async def mark_scene_completed(self, db: Session, scene_uuid: uuid.UUID, story_id: int) -> Optional[Scene]:
        """Mark a scene as completed and return the updated scene"""
        scene = scenes.mark_scene_as_completed(db, scene_uuid, story_id)
        
        if not scene:
            return None
        
        # Process the completed scene
        scene_id = cast(int, scene.id)
        await self.process_completed_scene(db, scene_id)
        
        return scene
    
    async def process_completed_scene(self, db: Session, scene_id: int) -> None:
        """Process a completed scene to analyze interactions and prepare for next scene generation"""
        scene_model = scenes.get_scene_with_messages(db, scene_id)
        
        if scene_model is None:
            return
            
        if getattr(scene_model, "status") != "completed":
            return

        scene_schema = SceneSchema.model_validate(scene_model)
        
        messages = scene_schema.messages
        
        if not messages:
            return
        
        summary_text = await self._summarize_scene_messages(db, messages)
        
        scenes.update_scene_summary(db, scene_id, summary_text)
    
    def _format_messages_for_llm(self, db: Session, messages: List[MessageSchema]) -> str:
        """
        Format messages from a scene for LLM processing, grouped by character.
        
        Args:
            db: Database session
            messages: List of MessageSchema objects from the scene
            
        Returns:
            A markdown-formatted string with messages grouped by character
        """
        # Group messages by character_id
        messages_by_character: Dict[int, List[MessageSchema]] = {}
        
        for message in messages:
            if message.character_id not in messages_by_character:
                messages_by_character[message.character_id] = []
            messages_by_character[message.character_id].append(message)
        
        # Format messages for each character
        formatted_sections: List[str] = []
        
        for character_id, char_messages in messages_by_character.items():
            # Skip if no messages
            if not char_messages:
                continue
                
            # Get character details
            character = get_character(db, character_id) if character_id else None
            
            if character is None:
                raise ValueError(f"Character with ID {character_id} not found")
            
            # Create header for this character
            section = f"# {character.name}\n"
            
            # Format each message
            for msg in char_messages:
                section += f"{msg.role}: {msg.content}\n"
            
            formatted_sections.append(section)
        
        # Join all sections with double newlines
        return "\n\n".join(formatted_sections) if formatted_sections else ""


    async def _summarize_scene_messages(self, db: Session, messages: List[MessageSchema]) -> str:
        """
        Analyze messages from a scene and generate a summary using LLM.
        
        This method will:
        - Extract key events and decisions from the scene
        - Identify important character interactions
        - Analyze sentiment and relationship changes (as interpreted by the LLM)
        - Prepare context for the next scene generation by highlighting memorable facts.
        
        Args:
            db: Database session
            messages: List of MessageSchema objects from the scene
            
        Returns:
            A string containing the short summary of the scene.
        """
        formatted_messages = self._format_messages_for_llm(db, messages)
        
        prompt = f"""
Please provide a short summary of the following scene. 
Focus on key events, how interactions impact relationships between characters, and any important facts that should be remembered from this scene.
The summary should be a concise narrative.

Scene context:
{formatted_messages}
"""
        
        # Create a new list for LLM messages, not to be confused with the input 'messages'
        llm_api_messages = [
            self.llm_service.create_message("system", prompt)
            # No user message with formatted_messages directly here, it's part of the system prompt now.
            # If you intend to send the formatted messages as a separate user message, uncomment the next line.
            # self.llm_service.create_message("user", formatted_messages) 
        ]
        
        llm_response = await self.llm_service.generate_completion(
            messages=llm_api_messages,
            model=ModelName.GPT41_MINI, # Using a fast model for summarization
            temperature=0.5,
        )

        summary_str = await LLMService.extract_content(llm_response)
        
        return summary_str.strip() 