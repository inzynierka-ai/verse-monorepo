from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from fastapi import WebSocket
from sqlalchemy.orm import Session


class BaseMessageHandler(ABC):
    """
    Abstract base class for message handlers.
    Provides interface for handling specific message types.
    """
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the handler with a database session
        
        Args:
            db_session: SQLAlchemy Session for database operations
        """
        self.db_session = db_session
        
    @abstractmethod
    async def handle(self, message: Dict[str, Any], websocket: WebSocket) -> bool:
        """
        Handle a message if this handler can process it
        
        Args:
            message: The incoming message
            websocket: The client websocket
            
        Returns:
            bool: True if the message was handled, False otherwise
        """
        pass 