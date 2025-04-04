from abc import ABC, abstractmethod
from typing import Dict, Any
from fastapi import WebSocket


class BaseMessageHandler(ABC):
    """
    Abstract base class for message handlers.
    Provides interface for handling specific message types.
    """
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