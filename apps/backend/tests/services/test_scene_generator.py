import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import logging

from sqlalchemy.orm import Session
from app.services.scene_generator import SceneGeneratorAgent
from app.services.llm import LLMService
from app.schemas.scene_generator import SceneGenerationResult
from app.models.scene import Scene
from app.models.story import Story
from app.models.character import Character
from app.schemas.story_generation import Location, Character as CharacterSchema
from app.crud import scenes as scenes_crud


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service for testing"""
    llm_service = MagicMock(spec=LLMService)
    llm_service.generate_completion = AsyncMock()
    llm_service.extract_content = AsyncMock()
    return llm_service


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_story():
    """Create a mock story for testing"""
    story = MagicMock(spec=Story)
    story.id = 1
    story.uuid = str(uuid.uuid4())
    story.description = "Test story"
    return story


@pytest.fixture
def mock_player():
    """Create a mock player character for testing"""
    player = MagicMock(spec=Character)
    player.id = 1
    player.name = "Player"
    player.description = "Player character"
    return player


@pytest.mark.asyncio
class TestSceneGeneratorStatus:
    """Tests for scene status handling in the SceneGeneratorAgent"""
    
    async def test_scene_status_transitions(
        self, 
        mock_llm_service, 
        mock_db_session, 
        mock_story, 
        mock_player
    ):
        """Test scene status transitions during generation"""
        # Setup mock callbacks
        on_location_added = AsyncMock()
        on_character_added = AsyncMock()
        on_action_changed = AsyncMock()
        
        # Create generator agent
        generator = SceneGeneratorAgent(
            llm_service=mock_llm_service,
            story=mock_story,
            player=mock_player,
            on_location_added=on_location_added,
            on_character_added=on_character_added,
            on_action_changed=on_action_changed,
            db_session=mock_db_session
        )
        
        # Mock scene creation
        mock_scene = MagicMock(spec=Scene)
        mock_scene.id = 1
        
        # Mock the scene generation result
        mock_location = Location(
            name="Test Location",
            description="A test location",
            uuid=str(uuid.uuid4())
        )
        mock_character = CharacterSchema(
            name="Test Character",
            description="A test character",
            uuid=str(uuid.uuid4()),
            relationships=[]
        )
        mock_result = SceneGenerationResult(
            location=mock_location,
            characters=[mock_character],
            description="A test scene",
            steps_taken=10
        )
        
        # Mock the necessary CRUD operations
        with patch('app.services.scene_generator.LocationGenerator') as mock_location_generator:
            with patch('app.services.scene_generator.CharacterGenerator') as mock_character_generator:
                with patch('app.services.scene_generator.Langfuse'):
                    with patch.object(generator, '_run_agent_loop', return_value=mock_result):
                        with patch.object(scenes_crud, 'create_scene_placeholder', return_value=mock_scene):
                            with patch.object(scenes_crud, 'update_scene_status') as mock_update_status:
                                with patch.object(scenes_crud, 'finalize_generated_scene', return_value=mock_scene):
                                    # Execute
                                    await generator.generate_scene()
                                    
                                    # Verify scene status transitions
                                    status_calls = [call[0][2] for call in mock_update_status.call_args_list]
                                    
                                    # Should transition from generation_not_started -> generating -> active
                                    assert "generating" in status_calls
                                    assert "active" in status_calls
                                    assert status_calls[-1] == "active"  # Final status should be active
    
    async def test_scene_generation_error_handling(
        self, 
        mock_llm_service, 
        mock_db_session, 
        mock_story, 
        mock_player
    ):
        """Test scene status transitions during generation with error handling"""
        # Setup mock callbacks
        on_location_added = AsyncMock()
        on_character_added = AsyncMock()
        on_action_changed = AsyncMock()
        
        # Create generator agent
        generator = SceneGeneratorAgent(
            llm_service=mock_llm_service,
            story=mock_story,
            player=mock_player,
            on_location_added=on_location_added,
            on_character_added=on_character_added,
            on_action_changed=on_action_changed,
            db_session=mock_db_session
        )
        
        # Mock scene creation
        mock_scene = MagicMock(spec=Scene)
        mock_scene.id = 1
        
        # Mock the necessary CRUD operations, but make the agent_loop raise an exception
        with patch('app.services.scene_generator.LocationGenerator'):
            with patch('app.services.scene_generator.CharacterGenerator'):
                with patch('app.services.scene_generator.Langfuse'):
                    with patch.object(generator, '_run_agent_loop', side_effect=Exception("Test error")):
                        with patch.object(scenes_crud, 'create_scene_placeholder', return_value=mock_scene):
                            with patch.object(scenes_crud, 'update_scene_status') as mock_update_status:
                                with patch.object(logging, 'error') as mock_log_error:
                                    # Execute and expect exception to be caught inside
                                    try:
                                        await generator.generate_scene()
                                    except Exception:
                                        pytest.fail("Exception was not handled properly")
                                    
                                    # Verify scene status transitions
                                    status_calls = [call[0][2] for call in mock_update_status.call_args_list]
                                    
                                    # Should transition from generation_not_started -> generating -> failed
                                    assert "generating" in status_calls
                                    assert "failed" in status_calls 
                                    assert status_calls[-1] == "failed"  # Final status should be failed
                                    
                                    # Verify error was logged
                                    assert mock_log_error.called 