import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.game_engine.tools.location_generator import LocationGenerator
from app.schemas.story_generation import Location, Story, LocationFromLLM
from app.services.llm import LLMService


@pytest.fixture
def mock_llm_service() -> MagicMock:
    """Create a mock LLM service for testing."""
    llm_service = MagicMock(spec=LLMService)
    llm_service.create_message = MagicMock(return_value={"role": "user", "content": "test"})
    llm_service.generate_completion = AsyncMock()
    llm_service.extract_content = AsyncMock()
    return llm_service


@pytest.fixture
def location_generator(mock_llm_service: MagicMock) -> LocationGenerator:
    """Create a LocationGenerator instance with a mock LLM service."""
    return LocationGenerator(llm_service=mock_llm_service)


@pytest.fixture
def test_story() -> Story:
    """Create a test story."""
    return Story(
        description="A test story description",
        rules=["Rule 1", "Rule 2"],
    )


@pytest.mark.asyncio
async def test_generate_location(
    location_generator: LocationGenerator, 
    test_story: Story, 
    mock_llm_service: MagicMock
):
    """Test the generate_location method."""
    # Mock the LLM service responses
    location_description = "This is a detailed location description."
    location_json = """
    {
        "id": "loc123",
        "name": "Test Location",
        "description": "A beautiful test location with stunning views",
        "rules": ["No smoking", "Keep quiet"]
    }
    """
    image_prompt = "A detailed image of a beautiful test location with stunning mountain views."
    
    # Configure the mock for extract_content
    mock_llm_service.extract_content.side_effect = [
        location_description,
        location_json,
        image_prompt
    ]
    
    # Mock the JSONService.parse_and_validate_json_response
    # Use a LocationFromLLM instance without imagePrompt to prevent duplicate
    location_from_llm = LocationFromLLM(
        name="Test Location",
        description="A beautiful test location with stunning views",
        rules=["No smoking", "Keep quiet"],
    )
    
    # Use patch instead of monkeypatch.context
    with patch('app.utils.json_service.JSONService.parse_and_validate_json_response', 
              return_value=location_from_llm):
        
        # Call the method
        result = await location_generator.generate_location(test_story)
    
    # Assertions
    assert isinstance(result, Location)
    assert result.name == "Test Location"
    assert result.imagePrompt == image_prompt
    
    # Verify expected calls
    assert mock_llm_service.extract_content.call_count == 3 