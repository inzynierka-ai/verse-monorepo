from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional, Callable, Type
import json
import logging
from jose import jwt, JWTError  # Add JWT handling
import uuid  # Add uuid

from app.routers.game_ws.base import BaseMessageHandler
from app.routers.game_ws.handlers.initialization import GameInitializationHandler
from app.routers.game_ws.handlers.scene_generation import SceneGenerationHandler  # Import SceneGenerationHandler
from app.db.session import get_db, Session



from app.schemas.conversation import ClientMessage, ChatChunkMessage, ChatCompleteMessage, ErrorMessage
from app.crud.characters import get_character_by_uuid
from app.crud.scenes import get_scene_by_uuid
from app.services.conversation_service import ConversationService
from app.services.auth import ALGORITHM, SECRET_KEY
from app.services.users import get_user

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/game", tags=["game"])


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
            username: str | None = payload.get("sub")
            
            # Store user info in WebSocket state for later use
            websocket.state.username = username
            
            if self.db_session and username:
                # Here you can perform database operations like checking if user exists,
                # updating last login time, etc.
                logger.info(f"Database available for user authentication: {username}")
                user = get_user(self.db_session, username)
                if not user:
                    logger.error(f"User {username} not found in database for authentication")
                    await websocket.send_json({
                        "type": "AUTH_ERROR",
                        "payload": {"message": "User not found"}
                    })
                else:
                    websocket.state.user_id = user.id
            
            logger.info(f"User authenticated: {username}")
            print(f"WebSocket authenticated for user: {username}")
            
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
        handler_factory: Optional[Callable[[], Dict[str, Type[BaseMessageHandler]]]] = None,
        db_session: Optional[Session] = None
    ):
        """
        Initialize the game message handler with explicit dependency injection.
        
        Args:
            handlers: List of message handlers to use. If None, handlers will be created using handler_factory.
            handler_factory: Factory function that returns handler classes. If None, default handlers will be used.
            db_session: SQLAlchemy Session for database operations
        """
        self.handler_factory = handler_factory or self._default_handler_factory
        self.db_session = db_session
        
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
        }
    
    def _create_default_handlers(self) -> List[BaseMessageHandler]:
        """
        Create instances of the default handlers.
        
        Returns:
            List of handler instances
        """
        factory = self.handler_factory()
        return [
            factory["authentication"](db_session=self.db_session),  # Auth handler should be first
            factory["initialization"](db_session=self.db_session),
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


@router.websocket("/ws")
async def game_websocket(websocket: WebSocket):
    """WebSocket endpoint for general game communication (authentication, etc.)"""
    # Initialize user state
    websocket.state.username = "unknown"

    # Get database session (synchronous)
    db = next(get_db())
    logger.info(f"Database session created for general WS: {db}")

    # Create a handler with the database session for this connection
    handler = GameMessageHandler(db_session=db) # Pass db session

    await handler.connect(websocket)

    try:
        while True:
            print(f"Waiting for message from user: {getattr(websocket.state, 'username', 'unknown')}")
            # Receive and parse JSON message
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handler.handle_message(message, websocket)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "ERROR",
                    "payload": {"message": "Invalid JSON"}
                })
    except WebSocketDisconnect:
        handler.disconnect(websocket)
        logger.info(f"WebSocket disconnected for user: {getattr(websocket.state, 'username', 'unknown')}")
    except Exception:
        username = getattr(websocket.state, "username", "unknown")
        logger.exception(f"Unexpected error in WebSocket connection for user: {username}")
        handler.disconnect(websocket) # Ensure disconnection on error
    finally:
        # Close the database session
        if db: # Check if db was assigned
            db.close()
            logger.info(f"Database session closed for general WS connection of user: {getattr(websocket.state, 'username', 'unknown')}")


@router.websocket("/ws/stories/{story_uuid}/scene")
async def scene_generation_websocket(
    websocket: WebSocket,
    story_uuid: uuid.UUID,
):
    """WebSocket endpoint for scene generation communication."""
    logger.info(f"Initiating scene generation WS for story {story_uuid}")
    await websocket.accept() # Accept the connection first
    
    # Get database session (synchronous)
    db = next(get_db())
    logger.info(f"Database session created for scene generation WS: {db}")

    # Initialize websocket state
    websocket.state.username = "unknown"

    # Create and use an authentication handler
    auth_handler = AuthenticationHandler(db_session=db)
    
    try:
        # Wait for and process the authentication message
        data = await websocket.receive_text()
        try:
            message = json.loads(data)
            if not await auth_handler.handle(message, websocket):
                await websocket.send_json({
                    "type": "ERROR",
                    "payload": {"message": "Authentication required as first message"}
                })
                if db:
                    db.close()
                return
        except json.JSONDecodeError:
            await websocket.send_json({
                "type": "ERROR",
                "payload": {"message": "Invalid JSON in authentication message"}
            })
            if db:
                db.close()
            return
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected during authentication for story {story_uuid}")
        if db:
            db.close()
        return
    except Exception as e:
        logger.exception(f"Error during authentication for scene generation: {e}")
        if db:
            db.close()
        return
    
    # Check if we have a user_id after authentication
    username = getattr(websocket.state, "username", "unknown")
    user_id: int = getattr(websocket.state, "user_id", None) # type: ignore

    logger.info(f"User ID after authentication: {user_id}")
    
    if not username:
        logger.error(f"No username after authentication for scene generation WS for story {story_uuid}")
        await websocket.send_json({
            "type": "AUTH_ERROR",
            "payload": {"message": "Authentication failed"}
        })
        if db:
            db.close()
        return
    
    # Acknowledge scene generation is starting
    await websocket.send_json({
        "type": "SCENE_START",
        "payload": {"message": f"Scene generation starting for story {story_uuid}"}
    })
    
    logger.info(f"Starting scene generation for user {username} and story {story_uuid}")
    
    handler = SceneGenerationHandler(
        websocket=websocket,
        story_uuid=story_uuid,
        db_session=db,
        user_id=user_id
    )

    try:
        await handler.run()
    except WebSocketDisconnect:
        logger.info(f"Scene generation WS disconnected for story {story_uuid}")
        # Cleanup is handled within handler.run()'s finally block
    except Exception as e:
        logger.exception(f"Unexpected error in scene generation WS for story {story_uuid}: {e}")
        # Attempt to send error before closing
        try:
            await websocket.send_json({"type": "ERROR", "payload": {"message": "Internal server error during scene generation."}})
        except Exception:
            pass # Ignore if sending fails (connection might be closed)
    finally:
        # The handler manages its own cleanup including WebSocket closure
        # Ensure the database session provided by Depends is closed
        logger.info(f"Closing DB session for scene generation WS for story {story_uuid}")
        if db:
            db.close()


@router.websocket("/ws/scenes/{scene_uuid}/characters/{character_uuid}")
async def scene_websocket(websocket: WebSocket, scene_uuid: str, character_uuid: str):

    # Accept the WebSocket connection
    await websocket.accept()

    db = next(get_db())

    auth_handler = AuthenticationHandler(db_session=db)

    try:
        # Wait for and process the authentication message
        data = await websocket.receive_text()
        try:
            message = json.loads(data)
            if not await auth_handler.handle(message, websocket):
                await websocket.send_json({
                    "type": "ERROR",
                    "payload": {"message": "Authentication required as first message"}
                })
                if db:
                    db.close()
                return
        except json.JSONDecodeError:
            await websocket.send_json({
                "type": "ERROR",
                "payload": {"message": "Invalid JSON in authentication message"}
            })
            if db:
                db.close()
            return
    except WebSocketDisconnect:
        if db:
            db.close()
        return
    except Exception as e:
        logger.exception(f"Error during authentication for scene generation: {e}")
        if db:
            db.close()
        return


    conversation_service = ConversationService()

    # Fetch scene and character by their UUIDs
    scene = get_scene_by_uuid(db, scene_uuid)
    character = get_character_by_uuid(db, character_uuid)

    if not scene or not character:
        await websocket.send_json({
            "type": "ERROR",
            "payload": {"message": "Invalid scene or character"}
        })
        await websocket.close(code=1008)  # Policy violation: invalid scene or character
        return

    # Acknowledge successful connection setup
    await websocket.send_json({
        "type": "CONNECTION_READY",
        "payload": {"message": f"Ready for conversation with {character.name}"}
    })

    while True:
        # Receive message from client
        raw_message = await websocket.receive_text()

        try:
            message = ClientMessage.model_validate_json(raw_message)
        except Exception as e:
            error = ErrorMessage(
                type="error",
                content="Invalid message format",
                details=str(e)
            )
            await websocket.send_text(error.model_dump_json())
            continue

        # Verify scene ID matches
        if not conversation_service.verify_scene_id(message.sceneId, scene_uuid):
            error = ErrorMessage(
                type="error",
                content="Scene ID mismatch"
            )
            await websocket.send_text(error.model_dump_json())
            continue

        # Process the message and stream chunks back to the client
        async for chunk in await conversation_service.process_message(
            db=db,
            messages=message.messages,
            character=character,
            scene=scene
        ):
            chunk_message = ChatChunkMessage(
                type="chat_chunk",
                content=chunk
            )
            await websocket.send_text(chunk_message.model_dump_json())

        # Signal that the response is complete
        complete_message = ChatCompleteMessage(type="chat_complete")
        await websocket.send_text(complete_message.model_dump_json())
