"""
Tests for the game_ws base message handler
"""
import pytest
from unittest.mock import AsyncMock
from fastapi import WebSocket
from typing import Dict, Any

from app.routers.game_ws.base import BaseMessageHandler


class ConcreteHandler(BaseMessageHandler):
    """Concrete implementation of BaseMessageHandler for testing"""
    
    async def handle(self, message: Dict[str, Any], websocket: WebSocket) -> bool:
        """Concrete implementation of handle method"""
        return True


@pytest.mark.asyncio
async def test_base_message_handler_interface() -> None:
    """Test that a concrete implementation of BaseMessageHandler can be instantiated"""
    handler = ConcreteHandler()
    mock_websocket = AsyncMock(spec=WebSocket)
    
    # Verify that the handle method can be called
    result = await handler.handle({"type": "TEST"}, mock_websocket)
    assert result is True 