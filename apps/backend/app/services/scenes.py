from fastapi import WebSocket
from typing import AsyncGenerator
from app.schemas.scene import SceneMessage
from app.services.llm import LLMService
from app.crud.characters import get_character
from app.crud.locations import get_location
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

class SceneService:
    def __init__(self):
        self.llm_service = LLMService()

    @asynccontextmanager
    async def manage_websocket(self, websocket: WebSocket):
        """Manage WebSocket connection lifecycle"""
        try:
            await websocket.accept()
            yield
        finally:
            try:
                await websocket.close()
            except RuntimeError:
                # Ignore "Cannot call close once a close message has been sent" error
                pass

    async def load_character_prompt(self, db: Session, character_id: int, location_id: int) -> str:
        """Load character's system prompt from db and enhance it with location context"""
        character = get_character(db=db, character_id=character_id)
        location = get_location(db=db, location_id=location_id)
        
        if not character:
            raise ValueError(f"Character {character_id} not found")
        if not location:
            raise ValueError(f"Location {location_id} not found")
        
        base_prompt = character.prompt
                
        location_context = f"\nLocation Context:\nYou are in the {location.name}. {location.description}"
        return base_prompt + location_context
                

    async def process_message(self, message: SceneMessage, system_prompt: str) -> AsyncGenerator[str, None]:
        messages = [
            self.llm_service.create_message("system", system_prompt),
            self.llm_service.create_message("user", message.content)
        ]
        
        return await self.llm_service.generate_completion(
            messages=messages,
            stream=True
        )

    def get_character_analysis(self, db: Session, character_id: int) -> dict:
        character = get_character(db=db, character_id=character_id)
        return {
            "relationshipLevel": character.relationship_level,
            "availableActions": [
                {"name": "Talk"},
                {"name": "Leave"}
            ]
        }

    def verify_scene_id(self, message_scene_id: str, url_scene_id: str) -> bool:
        return message_scene_id == url_scene_id 