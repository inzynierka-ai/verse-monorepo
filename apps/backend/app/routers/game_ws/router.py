from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional, Callable, Type
import json
import logging
from jose import jwt, JWTError  # Add JWT handling

from app.routers.game_ws.base import BaseMessageHandler
from app.routers.game_ws.handlers.initialization import GameInitializationHandler
from app.services.auth import SECRET_KEY, ALGORITHM  # Import your security constants

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class AuthenticationHandler(BaseMessageHandler):
    """Handler for authentication messages"""
    
    async def handle(self, message: Dict[str, Any], websocket: WebSocket) -> bool:
        message_type = message.get("type")
        
        if message_type != "AUTHENTICATE":
            return False
        
        await self._handle_authenticate(message, websocket)
        return True
    
    async def _handle_authenticate(self, message: Dict[str, Any], websocket: WebSocket):
        """Process authentication request"""
        payload = message.get("payload", {})
        auth_header = payload.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            await websocket.send_json({
                "type": "AUTH_ERROR",
                "payload": {"message": "Invalid authentication format"}
            })
            return
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        try:
            # Decode the JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            username = payload.get("preferred_username", user_id)
            
            # Store user info in WebSocket state for later use
            websocket.state.user_id = user_id
            websocket.state.username = username
            
            logger.info(f"User authenticated: {username} (ID: {user_id})")
            print(f"WebSocket authenticated for user: {username} (ID: {user_id})")
            
            # Send success response
            await websocket.send_json({
                "type": "AUTH_SUCCESS",
                "payload": {"message": f"Authenticated as {username}"}
            })
        except JWTError:
            logger.warning("Invalid authentication token received")
            await websocket.send_json({
                "type": "AUTH_ERROR",
                "payload": {"message": "Invalid authentication token"}
            })
        except Exception as e:
            logger.exception("Authentication error")
            await websocket.send_json({
                "type": "AUTH_ERROR",
                "payload": {"message": f"Authentication error: {str(e)}"}
            })


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
            "initialization": GameInitializationHandler,
            "authentication": AuthenticationHandler
        }
    
    def _create_default_handlers(self) -> List[BaseMessageHandler]:
        """
        Create instances of the default handlers.
        
        Returns:
            List of handler instances
        """
        factory = self.handler_factory()
        return [
            factory["authentication"](),  # Auth handler should be first
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
        username = getattr(websocket.state, "username", "unknown")
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed for user: {username}")
    
    async def handle_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Route incoming message to appropriate handler based on type"""
        message_type = message.get("type")
        username = getattr(websocket.state, "username", "unknown")
        print(f"Handling message {message_type} from user: {username}")
        
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
                logger.exception(f"Error in handler for message type {message_type} from user {username}")
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
    # Initialize user state
    websocket.state.user_id = None
    websocket.state.username = "unknown"
    
    await game_handler.connect(websocket)
    
    try:
        while True:
            print(f"Waiting for message from user: {getattr(websocket.state, 'username', 'unknown')}")
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
        username = getattr(websocket.state, "username", "unknown")
        logger.exception(f"Unexpected error in WebSocket connection for user: {username}")
        game_handler.disconnect(websocket)