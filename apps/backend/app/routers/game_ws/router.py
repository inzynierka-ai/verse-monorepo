from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional, Callable, Type
import json
import logging

from app.routers.game_ws.base import BaseMessageHandler
from app.routers.game_ws.handlers.initialization import GameInitializationHandler

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class GameMessageHandler:
    """
    Message router that delegates messages to specialized handlers.
    """
    def __init__(
        self, 
        handlers: Optional[List[BaseMessageHandler]] = None,
        handler_factory: Optional[Callable[[], Dict[str, Type[BaseMessageHandler]]]] = None
    ):
        """
        Initialize the game message handler with explicit dependency injection.
        
        Args:
            handlers: List of message handlers to use. If None, handlers will be created using handler_factory.
            handler_factory: Factory function that returns handler classes. If None, default handlers will be used.
        """
        self.handler_factory = handler_factory or self._default_handler_factory
        
        # Initialize handlers
        self.handlers: List[BaseMessageHandler] = handlers or self._create_default_handlers()
        
        # Track active connections
        self.active_connections: List[WebSocket] = []
    
    def _default_handler_factory(self) -> Dict[str, Type[BaseMessageHandler]]:
        """
        Default factory that provides the handler classes to instantiate.
        This makes testing easier by allowing replacement of this method.
        
        Returns:
            Dictionary of handler name to handler class
        """
        return {
            "initialization": GameInitializationHandler
        }
    
    def _create_default_handlers(self) -> List[BaseMessageHandler]:
        """
        Create instances of the default handlers.
        
        Returns:
            List of handler instances
        """
        factory = self.handler_factory()
        return [
            factory["initialization"](),
            # Add more handlers here as they're implemented
        ]
    
    async def connect(self, websocket: WebSocket):
        """Accept and track a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New WebSocket connection established")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("WebSocket connection closed")
    
    async def handle_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Route incoming message to appropriate handler based on type"""
        message_type = message.get("type")
        
        if not message_type:
            await websocket.send_json({
                "type": "ERROR",
                "payload": {"message": "Missing message type"}
            })
            return
        
        # Try each handler until one handles the message
        for handler in self.handlers:
            try:
                was_handled = await handler.handle(message, websocket)
                if was_handled:
                    return
            except Exception as e:
                logger.exception(f"Error in handler for message type {message_type}")
                await websocket.send_json({
                    "type": "ERROR",
                    "payload": {"message": str(e)}
                })
                return
        
        # If we got here, no handler processed the message
        await websocket.send_json({
            "type": "ERROR",
            "payload": {"message": f"Unknown message type: {message_type}"}
        })


# Create a single instance of the handler
game_handler = GameMessageHandler()


@router.websocket("/ws/game")
async def game_websocket(websocket: WebSocket):
    """WebSocket endpoint for game communication"""
    await game_handler.connect(websocket)
    
    try:
        while True:
            # Receive and parse JSON message
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await game_handler.handle_message(message, websocket)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "ERROR",
                    "payload": {"message": "Invalid JSON"}
                })
    except WebSocketDisconnect:
        game_handler.disconnect(websocket)
    except Exception:
        logger.exception("Unexpected error in WebSocket connection")
        game_handler.disconnect(websocket) 