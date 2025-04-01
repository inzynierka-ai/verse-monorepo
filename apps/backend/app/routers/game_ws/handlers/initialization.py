from typing import Dict, Any, Set, Optional
import logging

from fastapi import WebSocket
from pydantic import ValidationError

from app.schemas.world_generation import WorldGenerationInput, World, Character
from app.services.game_engine.orchestrators.game_initializer import GameInitializer
from app.routers.game_ws.base import BaseMessageHandler

# Set up logging
logger = logging.getLogger(__name__)


class GameInitializationHandler(BaseMessageHandler):
    """
    Handles game initialization messages.
    """
    def __init__(self, game_initializer: Optional[GameInitializer] = None):
        """
        Initialize the handler with explicit dependency injection.
        
        Args:
            game_initializer: GameInitializer instance to use. If None, a new instance will be created.
        """
        self.game_initializer = game_initializer or GameInitializer()
        self.message_types: Set[str] = {"INITIALIZE_GAME"}
    
    async def handle(self, message: Dict[str, Any], websocket: WebSocket) -> bool:
        message_type = message.get("type")
        
        if message_type not in self.message_types:
            return False
        
        if message_type == "INITIALIZE_GAME":
            await self._handle_initialize_game(message, websocket)
        
        return True
    
    async def _handle_initialize_game(self, message: Dict[str, Any], websocket: WebSocket):
        """
        Handle game initialization request
        1. Validate the WorldGenerationInput
        2. Generate world and send it to client
        3. Generate character and send it to client
        """
        try:
            # Validate input
            payload = message.get("payload", {})
            input_data = WorldGenerationInput(**payload)
            
            # Send status update
            await websocket.send_json({
                "type": "STATUS_UPDATE",
                "payload": {"status": "GENERATING_WORLD", "message": "Generating game world..."}
            })
            
            # Define callbacks for real-time updates
            async def on_world_generated(world: World):
                await websocket.send_json({
                    "type": "WORLD_CREATED",
                    "payload": world.model_dump()
                })
                await websocket.send_json({
                    "type": "STATUS_UPDATE",
                    "payload": {"status": "GENERATING_CHARACTER", "message": "Creating player character..."}
                })
            
            async def on_character_generated(character: Character):
                await websocket.send_json({
                    "type": "CHARACTER_CREATED",
                    "payload": character.model_dump()
                })
            
            # Start game initialization with callbacks
            await self.game_initializer.initialize_game(
                input_data,
                on_world_generated=on_world_generated,
                on_character_generated=on_character_generated
            )
            
            # Send initialization complete message
            await websocket.send_json({
                "type": "INITIALIZATION_COMPLETE",
                "payload": {"message": "Game initialization complete"}
            })
            
        except ValidationError as e:
            await websocket.send_json({
                "type": "ERROR",
                "payload": {"message": "Invalid input data", "details": e.errors()}
            })
        except Exception as e:
            logger.exception("Error during game initialization")
            await websocket.send_json({
                "type": "ERROR",
                "payload": {"message": f"Game initialization failed: {str(e)}"}
            }) 