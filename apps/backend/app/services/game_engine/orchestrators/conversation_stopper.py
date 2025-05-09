from typing import Optional, Callable, Awaitable
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.game_engine.tools.world_entity_generator import WorldEntityGenerator
from app.services.game_engine.tools.character_memory import CharacterMemoryGenerator

class VectorDBService:
    """
    Service that coordinates what happens when player leaves a conversation view.

    This service is responsible for orchestrating actions taking place when a player leaves a conversation view.
    
    The VectorDBService delegates the actual generation work to specialized services:
    - CharacterMemoryGenerator for creating memories from conversation messages
    - world_entity_generator for generating glossary entries for world entities which appeared for the first time in a given conversation (NPCs, locations, etc.)
    
    Usage flow:
    1. User finished a conversation and leaves the view, this submits the messages to the service
    2. The service generates memories and glossary entries based on the conversation messages
    3. The service saves the generated memories and glossary entries to the database

    This approach enables a more dynamic, organic, and engaging storytelling experience for the player in which the game world evolves based on their interactions.
    """
    def __init__(
        self,
        world_entity_generator: Optional[WorldEntityGenerator] = None,
        character_memory_generator: Optional[CharacterMemoryGenerator] = None,
        db_session: Optional[Session] = None
    ):
        self.world_entity_generator = world_entity_generator or WorldEntityGenerator(db_session=db_session)
        self.character_memory_generator = character_memory_generator or CharacterMemoryGenerator(db_session=db_session)
        self.db_session = db_session
    
    async def initialize_game(
        self, 
        user_input: StoryGenerationInput,
        user_id: int,
        on_story_generated: Optional[Callable[[Story], Awaitable[None]]] = None,
        on_character_generated: Optional[Callable[[Character], Awaitable[None]]] = None,
        story_id: Optional[int] = None
    ) -> InitialGameState:
        """
        Creates the initial game state from user input.
        
        Args:
            user_input: User input containing story parameters and player character draft
            on_story_generated: Optional callback called immediately after story generation
            on_character_generated: Optional callback called immediately after character generation
            story_id: Optional ID of the story to associate characters with
            
        Returns:
            InitialGameState with generated story and player character
        """
        # 1. Generate the story first
        story = await self.story_generator.generate_story(user_id, user_input.story)
        
        # Call the callback if provided
        if on_story_generated:
            await on_story_generated(story)
        
        # 2. Generate the player character within the context of the story
        player_character = await self.character_generator.generate_character(
            user_input.playerCharacter,
            story,
            is_player=True
        )
        
        # Call the callback if provided
        if on_character_generated:
            await on_character_generated(player_character)
        
        # 3. Return the initial game state
        return InitialGameState(
            story=story,
            playerCharacter=player_character
        ) 