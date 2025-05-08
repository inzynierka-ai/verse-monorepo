import pytest
import uuid
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.services.scene_service import SceneService
from app.models.scene import Scene
from app.models.message import Message


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_scene():
    """Create a mock scene with basic attributes"""
    scene = MagicMock(spec=Scene)
    scene.id = 1
    scene.uuid = str(uuid.uuid4())
    scene.story_id = 1
    scene.status = "active"
    scene.messages = []
    return scene


@pytest.fixture
def scene_service():
    """Create a SceneService instance for testing"""
    return SceneService()


class TestSceneStatusTransitions:
    """Tests for scene status transitions in the SceneService"""

    def test_mark_scene_completed(self, scene_service, mock_db, mock_scene):
        """Test marking a scene as completed"""
        # Setup
        scene_uuid = uuid.UUID(mock_scene.uuid)
        story_id = mock_scene.story_id
        
        # Mock the CRUD operation
        with patch('app.crud.scenes.mark_scene_as_completed', return_value=mock_scene) as mock_mark_completed:
            with patch.object(scene_service, 'process_completed_scene') as mock_process:
                # Execute
                result = scene_service.mark_scene_completed(mock_db, scene_uuid, story_id)
                
                # Verify
                assert result == mock_scene
                mock_mark_completed.assert_called_once_with(mock_db, scene_uuid, story_id)
                mock_process.assert_called_once_with(mock_db, mock_scene.id)
    
    def test_mark_scene_completed_not_found(self, scene_service, mock_db):
        """Test marking a non-existent scene as completed"""
        # Setup
        scene_uuid = uuid.uuid4()
        story_id = 1
        
        # Mock the CRUD operation to return None (scene not found)
        with patch('app.crud.scenes.mark_scene_as_completed', return_value=None):
            # Execute
            result = scene_service.mark_scene_completed(mock_db, scene_uuid, story_id)
            
            # Verify
            assert result is None
    
    def test_process_completed_scene(self, scene_service, mock_db, mock_scene):
        """Test processing a completed scene"""
        # Setup
        mock_scene.status = "completed"
        message = MagicMock(spec=Message)
        message.character_id = 1
        mock_scene.messages = [message]
        
        # Mock the CRUD operations
        with patch('app.crud.scenes.get_scene_with_messages', return_value=mock_scene) as mock_get_scene:
            with patch('app.crud.scenes.create_or_update_scene_summary') as mock_update_summary:
                # Execute
                scene_service.process_completed_scene(mock_db, mock_scene.id)
                
                # Verify
                mock_get_scene.assert_called_once_with(mock_db, mock_scene.id)
                mock_update_summary.assert_called_once()
                # Check that summary_data contains expected keys
                summary_data = mock_update_summary.call_args[0][2]
                assert "total_messages" in summary_data
                assert "character_participation" in summary_data


class TestCompleteSceneFlow:
    """Tests for the complete scene flow from marking completed to processing"""
    
    def test_complete_flow(self, scene_service, mock_db, mock_scene):
        """Test the complete flow from marking a scene as completed to processing it"""
        # Setup
        scene_uuid = uuid.UUID(mock_scene.uuid)
        story_id = mock_scene.story_id
        mock_scene.status = "active"
        message = MagicMock(spec=Message)
        message.character_id = 1
        mock_scene.messages = [message]
        
        completed_scene = MagicMock(spec=Scene)
        completed_scene.id = mock_scene.id
        completed_scene.status = "completed"
        completed_scene.messages = mock_scene.messages
        
        # Mock the CRUD operations
        with patch('app.crud.scenes.mark_scene_as_completed', return_value=completed_scene) as mock_mark_completed:
            with patch('app.crud.scenes.get_scene_with_messages', return_value=completed_scene) as mock_get_scene:
                with patch('app.crud.scenes.create_or_update_scene_summary') as mock_update_summary:
                    # Execute
                    result = scene_service.mark_scene_completed(mock_db, scene_uuid, story_id)
                    
                    # Verify
                    assert result == completed_scene
                    assert result.status == "completed"
                    mock_mark_completed.assert_called_once_with(mock_db, scene_uuid, story_id)
                    mock_get_scene.assert_called_once_with(mock_db, completed_scene.id)
                    mock_update_summary.assert_called_once()


class TestErrorHandling:
    """Tests for error handling in the SceneService"""
    
    def test_process_uncompleted_scene(self, scene_service, mock_db, mock_scene):
        """Test processing a scene that is not completed"""
        # Setup
        mock_scene.status = "active"  # Not completed
        
        # Mock the CRUD operation
        with patch('app.crud.scenes.get_scene_with_messages', return_value=mock_scene) as mock_get_scene:
            # Execute
            scene_service.process_completed_scene(mock_db, mock_scene.id)
            
            # Verify that no further processing occurred
            mock_get_scene.assert_called_once_with(mock_db, mock_scene.id)
    
    def test_process_scene_without_messages(self, scene_service, mock_db, mock_scene):
        """Test processing a completed scene without messages"""
        # Setup
        mock_scene.status = "completed"
        mock_scene.messages = []  # No messages
        
        # Mock the CRUD operation
        with patch('app.crud.scenes.get_scene_with_messages', return_value=mock_scene) as mock_get_scene:
            with patch('app.crud.scenes.create_or_update_scene_summary') as mock_update_summary:
                # Execute
                scene_service.process_completed_scene(mock_db, mock_scene.id)
                
                # Verify that no summary was created
                mock_get_scene.assert_called_once_with(mock_db, mock_scene.id)
                mock_update_summary.assert_not_called()
    
    def test_process_missing_scene(self, scene_service, mock_db):
        """Test processing a scene that does not exist"""
        # Setup
        scene_id = 999  # Non-existent scene
        
        # Mock the CRUD operation to return None
        with patch('app.crud.scenes.get_scene_with_messages', return_value=None) as mock_get_scene:
            # Execute
            scene_service.process_completed_scene(mock_db, scene_id)
            
            # Verify that the function gracefully handled the missing scene
            mock_get_scene.assert_called_once_with(mock_db, scene_id) 