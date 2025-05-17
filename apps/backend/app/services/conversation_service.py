import logging
import json
from typing import List, AsyncGenerator, Dict, Any, Literal
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.services.llm import LLMService, ModelName
from app.models.character import Character
from app.models.scene import Scene
from app.services.world_entity_service import WorldEntityService
from app.services.memory_manager import MemoryManager
from datetime import datetime
from app.utils.embedding import simplify_text_for_embedding, get_embedding
import uuid
from langfuse.decorators import observe  # type: ignore

from app.services.moderations import ModerationsService

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self):
        self.llm_service = LLMService()
        self.moderation_service = ModerationsService(openai_client=self.llm_service.openai_client)
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
    
    @observe(name="process_message")
    async def process_message(self, db: Session, messages: List[Dict[str, Any]], 
                             character: Character, scene: Scene) -> AsyncGenerator[str, None]:
        """Process a message and generate a response"""
        latest_message = messages[-1]["content"]
        await self.save_message(
            db=db,
            scene_id=scene.id,
            character_id=character.id,
            content=latest_message,
            role="user"
        )
        violated_categories = await self.moderation_service.process_moderation(latest_message)
        if violated_categories:
            logger.warning(f"Violated categories: {violated_categories}")
        system_prompt = await self._build_character_prompt(db, character, scene)
        
        # Convert messages to the format expected by the LLM service
        formatted_messages = [
            self.llm_service.create_message("system", system_prompt)
        ]
        
        # Add conversation history
        for msg in messages:
            formatted_messages.append(self.llm_service.create_message(msg["role"], msg["content"]))
        
        # Prepare arguments for LLM service
        llm_args: Dict[str, Any] = {
            "messages": formatted_messages,
            "model": ModelName.GPT41_MINI,
            "temperature": 0.7,
            "stream": True,
        }

        if violated_categories:
            llm_args["metadata"] = {"violated_categories": json.dumps(violated_categories)}
        
        # Get streaming response from LLM
        response = await self.llm_service.generate_completion(**llm_args)
        
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
        
    
    
    async def _build_character_prompt(self, db:Session, character: Character, scene: Scene) -> str:
        """Build a system prompt for the character"""
        # Get location information
        story = scene.story

        player_character = next((char for char in scene.characters if char.role == "player"), None)
        player_name = player_character.name if player_character else "unknown player"

        simplified_last_message = await simplify_text_for_embedding(scene.messages[-1].content)
        logging.info(f"Simplified last message: {simplified_last_message}")
        last_message = scene.messages[-1].content
        last_message_embedding = get_embedding(simplified_last_message)

        # Get character memories
        memory_manager = MemoryManager(db_session=db)
        memories = await memory_manager.find_similar_memories(character_id=character.id, query=last_message, top_n=5) # type: ignore

        location_info = f"You are currently at {scene.location.name}. {scene.location.description}" if scene.location else ""
        # Get relevant world entities
        world_entity_service = WorldEntityService(db_session=db, story_id=scene.story_id) # type: ignore
        world_entities = await world_entity_service.get_relevant_world_entities(scene, simplified_last_message, last_message_embedding)


        character_prompt = f"""
        You are not a language model. You are a fully realized character in a fictional story titled "{story.title}".

        Your name is {character.name}. Here is your character description:
        {character.description}

        Your backstory:
        {character.backstory}

        Your personality traits:
        {character.personality_traits}  

        Your goals in the story:
        {character.goals}

        Your speaking style:
        {character.speaking_style}

        Your immediate goals for the current situation (These are very important and you should focus on achieving them now):
        {character.immediate_goals}

        You are in the following situation:
        {scene.description}

        You are currently speaking with the player character named {player_name}. Speak and act according to your personality, goals, and knowledge. Do **not** narrate or explain your behavior unless it's something your character would naturally do.

        Memories of past interactions (which you remember as real experiences):
        {chr(10).join([f"- {memory.memory_text}" for memory in memories])}
        
        Your current location:
        {location_info}

        Relevant world entities and lore:
        {chr(10).join([f"- {entity.name}: {entity.canonical_description}" for entity in world_entities])}

        Strict Rules:
        - Stay completely in character. Never refer to being an AI, LLM, or model.
        - Use language, tone, and knowledge consistent with your role in the story world.
        - Do not break the fourth wall.
        - Do not provide options, summaries, or meta-commentary unless it's something your character would naturally do.
        - Respond as if this world is real to you. Stay grounded in the current situation and your personality.
        - Do not make your part too long. Keep it really concise to maintain a quick back-and-forth with the player.
        - Avoid finishing senteces with questions.
        """

        # Combine character prompt with location information
        logging.info(f"Character prompt for {character.name}: {character_prompt}")
        return character_prompt
    
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