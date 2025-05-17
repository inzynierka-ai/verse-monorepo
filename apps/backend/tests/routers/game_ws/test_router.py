"""
Tests for the game_ws router
"""
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock

import pytest
from fastapi import WebSocket

from app.routers.game_ws.router import GameMessageHandler
from app.routers.game_ws.base import BaseMessageHandler


class MockHandler(BaseMessageHandler):
    """Mock message handler for testing"""
    
    def __init__(self, message_types: Optional[List[str]] = None):
        self.message_types = message_types or ["TEST_TYPE"]
        self.handle_called = False
        self.handle_mock = AsyncMock(return_value=True)
    
    async def handle(self, message: Dict[str, Any], websocket: WebSocket) -> bool:
        """Mock implementation that records call and delegates to mock"""
        self.handle_called = True
        return await self.handle_mock(message, websocket)


@pytest.fixture
def mock_websocket() -> AsyncMock:
    """Create a mock WebSocket for testing"""
    return AsyncMock(spec=WebSocket)


@pytest.fixture
def mock_handler() -> MockHandler:
    """Create a mock handler for testing"""
    return MockHandler()


@pytest.fixture
def game_handler(mock_handler: MockHandler) -> GameMessageHandler:
    """Create a GameMessageHandler with mock handlers for testing"""
    # Explicitly use dependency injection by passing handlers
    return GameMessageHandler(handlers=[mock_handler])


@pytest.mark.asyncio
async def test_connect(game_handler: GameMessageHandler, mock_websocket: AsyncMock) -> None:
    """Test WebSocket connection handling"""
    await game_handler.connect(mock_websocket)
    
    # Verify connection was accepted and tracked
    mock_websocket.accept.assert_called_once()
    assert mock_websocket in game_handler.active_connections


@pytest.mark.asyncio
async def test_disconnect(game_handler: GameMessageHandler, mock_websocket: AsyncMock) -> None:
    """Test WebSocket disconnection handling"""
    # Add websocket to active connections first
    await game_handler.connect(mock_websocket)
    assert mock_websocket in game_handler.active_connections
    
    # Test disconnect
    game_handler.disconnect(mock_websocket)
    assert mock_websocket not in game_handler.active_connections


@pytest.mark.asyncio
async def test_handle_message_missing_type(game_handler: GameMessageHandler, mock_websocket: AsyncMock) -> None:
    """Test handling message with missing type"""
    await game_handler.handle_message({}, mock_websocket)
    
    # Verify error response
    mock_websocket.send_json.assert_called_once()
    call_args = mock_websocket.send_json.call_args[0][0]
    assert call_args["type"] == "ERROR"
    assert "Missing message type" in call_args["payload"]["message"]


@pytest.mark.asyncio
async def test_handle_message_unknown_type(game_handler: GameMessageHandler, mock_websocket: AsyncMock) -> None:
    """Test handling message with unknown type"""
    # Set mock handler to only handle specific type
    game_handler.handlers[0].handle_mock.return_value = False
    
    await game_handler.handle_message({"type": "UNKNOWN_TYPE"}, mock_websocket)
    
    # Verify error response
    mock_websocket.send_json.assert_called_once()
    call_args = mock_websocket.send_json.call_args[0][0]
    assert call_args["type"] == "ERROR"
    assert "Unknown message type" in call_args["payload"]["message"]


@pytest.mark.asyncio
async def test_handle_message_handler_exception(game_handler: GameMessageHandler, mock_websocket: AsyncMock) -> None:
    """Test handling exception from message handler"""
    # Configure mock handler to raise exception
    game_handler.handlers[0].handle_mock.side_effect = Exception("Test error")
    
    await game_handler.handle_message({"type": "TEST_TYPE"}, mock_websocket)
    
    # Verify error response
    mock_websocket.send_json.assert_called_once()
    call_args = mock_websocket.send_json.call_args[0][0]
    assert call_args["type"] == "ERROR"
    assert "Test error" in call_args["payload"]["message"]


@pytest.mark.asyncio
async def test_handle_message_successful(game_handler: GameMessageHandler, mock_websocket: AsyncMock) -> None:
    """Test successful message handling"""
    await game_handler.handle_message({"type": "TEST_TYPE"}, mock_websocket)
    
    # Verify handler was called
    assert game_handler.handlers[0].handle_called
    game_handler.handlers[0].handle_mock.assert_called_once()
    
    # Verify no error response was sent
    mock_websocket.send_json.assert_not_called()


@pytest.mark.asyncio
async def test_multiple_handlers(mock_websocket: AsyncMock) -> None:
    """Test message routing with multiple handlers"""
    # Create handlers for different message types
    handler1 = MockHandler(message_types=["TYPE1"])
    handler1.handle_mock.return_value = False  # This handler doesn't handle the message
    
    handler2 = MockHandler(message_types=["TYPE2"])
    handler2.handle_mock.return_value = True  # This handler handles the message
    
    # Create game handler with both mock handlers using dependency injection
    game_handler = GameMessageHandler(handlers=[handler1, handler2])
    
    # Send message of type TYPE2
    await game_handler.handle_message({"type": "TYPE2"}, mock_websocket)
    
    # Verify both handlers were tried, but only handler2 actually handled it
    assert handler1.handle_called
    assert handler2.handle_called
    
    # No error response should be sent
    mock_websocket.send_json.assert_not_called()


@pytest.mark.asyncio
async def test_handler_factory() -> None:
    """Test the handler factory functionality"""
    # Create mock handlers
    mock_handler = MockHandler()

    # Create a custom factory
    def custom_factory() -> Dict[str, Any]:
        return {
            "initialization": lambda: mock_handler  # Must include the initialization key
        }
    
    # Create handler with custom factory but no explicit handlers
    handler = GameMessageHandler(handler_factory=custom_factory)
    
    # Verify custom factory was used
    assert handler.handlers[0] is mock_handler 