from typing import List, AsyncGenerator, Dict, Any, Literal
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.services.llm import LLMService, ModelName
from app.models.character import Character
from app.models.scene import Scene
from datetime import datetime
import uuid

class ConversationService:
    def __init__(self):
        self.llm_service = LLMService()
    
    async def manage_websocket(self, websocket: WebSocket):
        """Context manager for WebSocket connection handling"""
        await websocket.accept()
        try:
            yield
        finally:
            await websocket.close()
    
    def verify_scene_id(self, message_scene_id: str, current_scene_id: str) -> bool:
        """Verify that the scene ID in the message matches the current scene ID"""
        return message_scene_id == current_scene_id
    
    async def process_message(self, db: Session, messages: List[Dict[str, Any]], 
                             character: Character, scene: Scene) -> AsyncGenerator[str, None]:
        """Process a message and generate a response"""
        await self.save_message(
            db=db,
            scene_id=scene.id,
            character_id=character.id,
            content=messages[-1]["content"],
            role="user"
        )
        system_prompt = self._build_character_prompt(character, scene)
        
        # Convert messages to the format expected by the LLM service
        formatted_messages = [
            self.llm_service.create_message("system", system_prompt)
        ]
        
        # Add conversation history
        for msg in messages:
            formatted_messages.append(self.llm_service.create_message(msg["role"], msg["content"]))
        
        # Get streaming response from LLM
        response = await self.llm_service.generate_completion(
            messages=formatted_messages,
            model=ModelName.GPT41_MINI,
            temperature=0.7,
            stream=True
        )
        
        # Collect the full response while streaming chunks
        full_response = ""
        
        # Ensure we're always returning a generator
        if isinstance(response, AsyncGenerator):
            async def collect_and_stream() -> AsyncGenerator[str, None]:
                nonlocal full_response
                async for chunk in response:
                    full_response += chunk
                    yield chunk
                
                # Save the complete message after all chunks are processed
                await self.save_message(
                    db=db,
                    scene_id=scene.id,
                    character_id=character.id,
                    content=full_response,
                    role="assistant"
                )
            
            return collect_and_stream()
        else:
            # This branch should never be taken due to stream=True
            # but it's here to satisfy the type checker
            async def single_value_generator() -> AsyncGenerator[str, None]:
                response_text = str(response)
                yield response_text
                
                # Save the complete message
                await self.save_message(
                    db=db,
                    scene_id=scene.id,
                    character_id=character.id,
                    content=response_text,
                    role="assistant"
                )
                
            return single_value_generator()
    
    def _build_character_prompt(self, character: Character, scene: Scene) -> str:
        """Build a system prompt for the character"""
        # Get location information
        location_info = f"You are currently at {scene.location.name}. {scene.location.description}" if scene.location else ""
        
        # Combine character prompt with location information
        return f"{character.description}\n\n{location_info}\n\nRemember to stay in character at all times."
    
    async def save_message(self, db: Session, scene_id: Any, 
                         character_id: Any, content: str, role: Literal["user", "assistant", "system"]) -> Dict[str, Any]:
        """Save a message to the database"""
        from app.crud.messages import create_message
        from app.schemas.message import MessageCreate
        
        # Make sure we have integer values for IDs
        # This safely handles both direct integers and SQLAlchemy Column/objects
        scene_id_value = getattr(scene_id, "value", scene_id)
        if hasattr(scene_id, "id"):
            scene_id_value = scene_id.id
            
        character_id_value = getattr(character_id, "value", character_id)
        if hasattr(character_id, "id"):
            character_id_value = character_id.id
        
        message = MessageCreate(
            scene_id=scene_id_value,
            character_id=character_id_value,
            content=content,
            role=role,
            timestamp=datetime.now(),
            uuid=str(uuid.uuid4())
        )
        
        return create_message(db, message) 