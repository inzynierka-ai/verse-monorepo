"""
Tests for the GameInitializationHandler
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket
from pydantic import ValidationError
from typing import Dict, Any, List, cast

from app.routers.game_ws.handlers.initialization import GameInitializationHandler
from app.schemas.world_generation import World, Character


@pytest.fixture
def handler() -> GameInitializationHandler:
    """Create a GameInitializationHandler for testing"""
    return GameInitializationHandler()


@pytest.fixture
def mock_websocket() -> AsyncMock:
    """Create a mock WebSocket for testing"""
    return AsyncMock(spec=WebSocket)


@pytest.fixture
def sample_world() -> World:
    """Create a sample world for testing"""
    return World(
        description="A post-apocalyptic world devastated by climate change",
        rules=["Resources are scarce", "Technology is rare"]
    )


@pytest.fixture
def sample_character() -> Character:
    """Create a sample character for testing"""
    return Character(
        name="Test Character",
        description="A survivor in the wasteland",
        personalityTraits=["Brave", "Resourceful"],
        backstory="Grew up in an underground bunker",
        goals=["Find water", "Establish a safe settlement"],
        relationships=[],
        imagePrompt="A rugged survivor with tattered clothes",
        role="player"
    )


@pytest.mark.asyncio
async def test_handle_filters_message_types(
    handler: GameInitializationHandler,
    mock_websocket: AsyncMock
) -> None:
    """Test that the handler only processes relevant message types"""
    # Test with wrong message type
    result = await handler.handle({"type": "WRONG_TYPE"}, mock_websocket)
    assert result is False
    mock_websocket.send_json.assert_not_called()
    
    # Test with correct message type
    with patch.object(handler, '_handle_initialize_game', new_callable=AsyncMock) as mock_handle:
        result = await handler.handle({"type": "INITIALIZE_GAME"}, mock_websocket)
        assert result is True
        mock_handle.assert_called_once()


@pytest.mark.asyncio
async def test_handle_initialize_game_validation_error(
    handler: GameInitializationHandler,
    mock_websocket: AsyncMock
) -> None:
    """Test validation error handling in initialization handler"""
    # Prepare invalid input message (missing required fields)
    invalid_message: Dict[str, Any] = {
        "type": "INITIALIZE_GAME",
        "payload": {}
    }
    
    await handler._handle_initialize_game(invalid_message, mock_websocket)
    
    # Verify error response
    mock_websocket.send_json.assert_called_once()
    call_args = mock_websocket.send_json.call_args[0][0]
    assert call_args["type"] == "ERROR"
    assert "Invalid input data" in call_args["payload"]["message"]


@pytest.mark.asyncio
async def test_handle_initialize_game_exception(
    handler: GameInitializationHandler,
    mock_websocket: AsyncMock
) -> None:
    """Test exception handling in initialization handler"""
    # Mock GameInitializer to raise an exception
    with patch.object(handler, 'game_initializer') as mock_initializer:
        mock_initializer.initialize_game.side_effect = Exception("Test error")
        
        # Prepare valid input message
        valid_message: Dict[str, Any] = {
            "type": "INITIALIZE_GAME",
            "payload": {
                "world": {
                    "theme": "fantasy", 
                    "genre": "medieval",
                    "year": 1200,
                    "setting": "kingdom"
                },
                "playerCharacter": {
                    "name": "Test",
                    "age": 25,
                    "appearance": "Tall with brown hair",
                    "background": "Former knight"
                }
            }
        }
        
        await handler._handle_initialize_game(valid_message, mock_websocket)
        
        # Verify error response
        calls = mock_websocket.send_json.call_args_list
        assert len(calls) >= 1
        last_call = calls[-1][0][0]
        assert last_call["type"] == "ERROR"
        assert "Game initialization failed" in last_call["payload"]["message"]


@pytest.mark.asyncio
async def test_handle_initialize_game_callbacks(
    handler: GameInitializationHandler,
    mock_websocket: AsyncMock,
    sample_world: World,
    sample_character: Character
) -> None:
    """Test that callbacks are executed properly during initialization"""
    # Mock GameInitializer
    with patch.object(handler, 'game_initializer') as mock_initializer:
        # Set up side effect to call the callbacks
        async def simulate_callbacks(input_data, on_world_generated, on_character_generated):
            await on_world_generated(sample_world)
            await on_character_generated(sample_character)
            return None
        
        mock_initializer.initialize_game.side_effect = simulate_callbacks
        
        # Prepare valid input message
        valid_message: Dict[str, Any] = {
            "type": "INITIALIZE_GAME",
            "payload": {
                "world": {
                    "theme": "fantasy", 
                    "genre": "medieval",
                    "year": 1200,
                    "setting": "kingdom"
                },
                "playerCharacter": {
                    "name": "Test",
                    "age": 25,
                    "appearance": "Tall with brown hair",
                    "background": "Former knight"
                }
            }
        }
        
        await handler._handle_initialize_game(valid_message, mock_websocket)
        
        # Verify messages sent via callbacks
        calls = mock_websocket.send_json.call_args_list
        assert len(calls) >= 4  # At least 4 messages should be sent
        
        # First message: STATUS_UPDATE (GENERATING_WORLD)
        assert calls[0][0][0]["type"] == "STATUS_UPDATE"
        assert calls[0][0][0]["payload"]["status"] == "GENERATING_WORLD"
        
        # Second message: WORLD_CREATED
        assert calls[1][0][0]["type"] == "WORLD_CREATED"
        assert "description" in calls[1][0][0]["payload"]
        
        # Third message: STATUS_UPDATE (GENERATING_CHARACTER)
        assert calls[2][0][0]["type"] == "STATUS_UPDATE"
        assert calls[2][0][0]["payload"]["status"] == "GENERATING_CHARACTER"
        
        # Fourth message: CHARACTER_CREATED
        assert calls[3][0][0]["type"] == "CHARACTER_CREATED"
        assert "name" in calls[3][0][0]["payload"]
        
        # Final message: INITIALIZATION_COMPLETE
        assert calls[4][0][0]["type"] == "INITIALIZATION_COMPLETE" 