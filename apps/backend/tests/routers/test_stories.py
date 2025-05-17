import pytest
import uuid
from unittest.mock import patch, MagicMock

from app.models.scene import Scene
from app.services.scene_service import SceneService


@pytest.mark.parametrize(
    "story_uuid,scene_uuid,expected_status,expected_detail",
    [
        (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            200,
            None,
        ),
        (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            404,
            "Scene not found or already completed",
        ),
    ],
)
def test_complete_scene(
    test_client,
    story_uuid,
    scene_uuid,
    expected_status,
    expected_detail,
):
    """Test the complete scene endpoint with various scenarios"""
    
    # Mock the SceneService and story verification
    with patch("app.routers.stories.get_story") as mock_get_story:
        with patch.object(SceneService, "mark_scene_completed") as mock_mark_completed:
            # Setup story mock
            mock_story = MagicMock()
            mock_story.id = 1
            mock_get_story.return_value = mock_story
            
            # Setup scene mock
            if expected_status == 200:
                mock_scene = MagicMock(spec=Scene)
                mock_scene.id = 1
                mock_scene.uuid = scene_uuid
                mock_scene.status = "completed"
                mock_mark_completed.return_value = mock_scene
            else:
                mock_mark_completed.return_value = None
            
            # Make request
            response = test_client.patch(
                f"/api/v1/stories/{story_uuid}/scenes/{scene_uuid}/complete", 
            )
            
            # Verify
            assert response.status_code == expected_status
            
            if expected_status == 200:
                # Successful response should contain scene data
                assert response.json()["uuid"] == scene_uuid
                assert response.json()["status"] == "completed"
            else:
                # Error response should contain expected detail
                assert response.json()["detail"] == expected_detail


def test_complete_scene_integration(test_client):
    """Test the complete scene flow in integration with other endpoints"""
    
    # Create mocks for the required services and models
    with patch("app.routers.stories.get_story") as mock_get_story:
        with patch.object(SceneService, "mark_scene_completed") as mock_mark_completed:
            with patch.object(SceneService, "fetch_latest_active_scene") as mock_fetch_scene:
                # Setup mocks
                story_uuid = str(uuid.uuid4())
                scene_uuid = str(uuid.uuid4())
                
                # Story mock
                mock_story = MagicMock()
                mock_story.id = 1
                mock_story.uuid = story_uuid
                mock_get_story.return_value = mock_story
                
                # Active scene mock
                active_scene = MagicMock(spec=Scene)
                active_scene.id = 1
                active_scene.uuid = scene_uuid
                active_scene.status = "active"
                active_scene.story_id = 1
                
                # Completed scene mock
                completed_scene = MagicMock(spec=Scene)
                completed_scene.id = 1
                completed_scene.uuid = scene_uuid
                completed_scene.status = "completed"
                completed_scene.story_id = 1
                
                # Configure mock behaviors
                mock_fetch_scene.side_effect = [
                    active_scene,  # First call returns the active scene
                    None,         # Second call returns None (no active scene)
                ]
                mock_mark_completed.return_value = completed_scene
                
                # Test scenario: fetch active scene, complete it, verify no active scene
                
                # Step 1: Get latest active scene
                response = test_client.get(f"/api/v1/stories/{story_uuid}/scenes/latest")
                assert response.status_code == 200
                assert response.json()["status"] == "active"
                
                # Step 2: Complete the scene
                response = test_client.patch(
                    f"/api/v1/stories/{story_uuid}/scenes/{scene_uuid}/complete"
                )
                assert response.status_code == 200
                assert response.json()["status"] == "completed"
                
                # Step 3: Try to get latest active scene again (should return 404)
                response = test_client.get(f"/api/v1/stories/{story_uuid}/scenes/latest")
                assert response.status_code == 404
                assert "detail" in response.json() 