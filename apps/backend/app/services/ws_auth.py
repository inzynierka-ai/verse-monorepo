import logging
import json
from typing import Optional
from fastapi import WebSocket
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.services.auth import SECRET_KEY, ALGORITHM
from app.services.users import get_user

# Set up logging
logger = logging.getLogger(__name__)

class WebSocketAuthenticator:
    """
    Reusable authentication handler for WebSocket connections
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the WebSocket authenticator
        
        Args:
            db_session: SQLAlchemy database session for user lookups
        """
        self.db_session = db_session
    
    async def authenticate(self, websocket: WebSocket) -> bool:
        """
        Authenticate a WebSocket connection using JWT token
        
        Args:
            websocket: The WebSocket connection to authenticate
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        try:
            # Wait for authentication message
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") != "AUTHENTICATE":
                    await websocket.send_json({
                        "type": "ERROR",
                        "payload": {"message": "Authentication required as first message"}
                    })
                    return False
                
                # Extract token from payload
                payload = message.get("payload", {})
                auth_header = payload.get("Authorization", "")
                
                if not auth_header.startswith("Bearer "):
                    await websocket.send_json({
                        "type": "AUTH_ERROR",
                        "payload": {"message": "Invalid authentication format"}
                    })
                    return False
                
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                
                # Decode the JWT token
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username: str | None = payload.get("sub")
                
                # Store user info in WebSocket state
                websocket.state.username = username
                
                if self.db_session and username:
                    # Perform database operations like checking if user exists
                    user = get_user(self.db_session, username)
                    if not user:
                        logger.error(f"User {username} not found in database for authentication")
                        await websocket.send_json({
                            "type": "AUTH_ERROR",
                            "payload": {"message": "User not found"}
                        })
                        return False
                    websocket.state.user_id = user.id
                
                logger.info(f"User authenticated: {username}")
                
                # Send success response
                await websocket.send_json({
                    "type": "AUTH_SUCCESS",
                    "payload": {"message": f"Authenticated as {username}"}
                })
                return True
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "ERROR",
                    "payload": {"message": "Invalid JSON in authentication message"}
                })
                return False
            except JWTError:
                logger.warning("Invalid authentication token received")
                await websocket.send_json({
                    "type": "AUTH_ERROR",
                    "payload": {"message": "Invalid authentication token"}
                })
                return False
        except Exception as e:
            logger.exception(f"Authentication error: {e}")
            await websocket.send_json({
                "type": "AUTH_ERROR",
                "payload": {"message": f"Authentication error: {str(e)}"}
            })
            return False 