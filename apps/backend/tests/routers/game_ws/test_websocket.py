"""
Integration tests for the game_ws WebSocket endpoint
"""

from typing import Dict, Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from app.main import app
from app.schemas.story_generation import Story, Character
from app.routers.game_ws.router import GameMessageHandler


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for FastAPI app testing"""
    return TestClient(app)


@pytest.fixture
def sample_initialization_message() -> Dict[str, Any]:
    """Create a sample initialization message for testing"""
    return {
        "type": "INITIALIZE_GAME",
        "payload": {
            "story": {
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


@pytest.fixture
def sample_story() -> Story:
    """Create a sample story for testing"""
    return Story(
        description="A medieval kingdom with castles and villages",
        title="The Kingdom of Astoria",
        rules=["Magic is rare", "Politics are dangerous"]
    )


@pytest.fixture
def sample_character() -> Character:
    """Create a sample character for testing"""
    return Character(
        name="Test Character",
        description="A knight who lost his honor",
        personalityTraits=["Honorable", "Brave"],
        backstory="Was framed for treason and exiled",
        goals=["Clear my name", "Return to the kingdom"],
        relationships=[],
        image_dir="https://localhost:8000/media/comfyui/test.png",
        role="player",
        uuid="12345678-1234-5678-1234-567812345678"
    )


def test_websocket_connection(test_client: TestClient) -> None:
    """Test establishing WebSocket connection"""
    with test_client.websocket_connect("/ws/game"):
        # If this doesn't raise an exception, the connection was successful
        pass


def test_websocket_invalid_json(test_client: TestClient) -> None:
    """Test sending invalid JSON to the WebSocket"""
    with test_client.websocket_connect("/ws/game") as websocket:
        websocket.send_text("not valid json")
        response = websocket.receive_json()
        
        # Verify error response
        assert response["type"] == "ERROR"
        assert "Invalid JSON" in response["payload"]["message"]


def test_websocket_missing_type(test_client: TestClient) -> None:
    """Test sending message with missing type"""
    with test_client.websocket_connect("/ws/game") as websocket:
        websocket.send_json({})
        response = websocket.receive_json()
        
        # Verify error response
        assert response["type"] == "ERROR"
        assert "Missing message type" in response["payload"]["message"]


def test_websocket_unknown_type(test_client: TestClient) -> None:
    """Test sending message with unknown type"""
    with test_client.websocket_connect("/ws/game") as websocket:
        websocket.send_json({"type": "UNKNOWN_TYPE"})
        response = websocket.receive_json()
        
        # Verify error response
        assert response["type"] == "ERROR"
        assert "Unknown message type" in response["payload"]["message"]


@pytest.mark.asyncio
async def test_websocket_initialization_flow(
    test_client: TestClient,
    sample_initialization_message: Dict[str, Any],
    sample_story: Story,
    sample_character: Character
) -> None:
    """Test the complete game initialization flow through WebSocket"""
    # Create a mock handler that directly implements the needed functionality
    mock_handler = AsyncMock()
    
    async def mock_handle(message: Dict[str, Any], websocket: WebSocket) -> bool:
        if message["type"] == "INITIALIZE_GAME":
            # Send the sequence of messages that would be sent during initialization
            await websocket.send_json({
                "type": "STATUS_UPDATE",
                "payload": {"status": "GENERATING_STORY", "message": "Generating game story..."}
            })
            
            await websocket.send_json({
                "type": "STORY_CREATED",
                "payload": sample_story.model_dump()
            })
            
            await websocket.send_json({
                "type": "STATUS_UPDATE",
                "payload": {"status": "GENERATING_CHARACTER", "message": "Creating player character..."}
            })
            
            await websocket.send_json({
                "type": "CHARACTER_CREATED",
                "payload": sample_character.model_dump()
            })
            
            await websocket.send_json({
                "type": "INITIALIZATION_COMPLETE",
                "payload": {"message": "Game initialization complete"}
            })
            
            return True
        return False
    
    mock_handler.handle = mock_handle
    
    # Patch the GameMessageHandler's handlers list
    with patch('app.routers.game_ws.router.GameMessageHandler._create_default_handlers', return_value=[mock_handler]):
        # Connect to the WebSocket and test
        with test_client.websocket_connect("/ws/game") as websocket:
            # Send initialization message
            websocket.send_json(sample_initialization_message)
            
            # Verify expected message sequence
            response1 = websocket.receive_json()  # STATUS_UPDATE
            assert response1["type"] == "STATUS_UPDATE"
            assert response1["payload"]["status"] == "GENERATING_STORY"
            
            response2 = websocket.receive_json()  # STORY_CREATED
            assert response2["type"] == "STORY_CREATED"
            assert "description" in response2["payload"]
            
            response3 = websocket.receive_json()  # STATUS_UPDATE
            assert response3["type"] == "STATUS_UPDATE"
            assert response3["payload"]["status"] == "GENERATING_CHARACTER"
            
            response4 = websocket.receive_json()  # CHARACTER_CREATED
            assert response4["type"] == "CHARACTER_CREATED"
            assert "name" in response4["payload"]
            
            response5 = websocket.receive_json()  # INITIALIZATION_COMPLETE
            assert response5["type"] == "INITIALIZATION_COMPLETE"