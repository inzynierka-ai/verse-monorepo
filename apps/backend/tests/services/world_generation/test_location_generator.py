import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.world_generation.location_generator import LocationGenerator
from app.schemas.world_generation import Location, World
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
def test_world() -> World:
    """Create a test world."""
    return World(
        description="A test world description",
        rules=["Rule 1", "Rule 2"],
        prolog="Once upon a time...",
    )


@pytest.mark.asyncio
async def test_generate_location(
    location_generator: LocationGenerator, 
    test_world: World, 
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
    
    # Mocking the JSON parsing result
    location_obj = Location(
        id="loc123",
        name="Test Location",
        description="A beautiful test location with stunning views",
        rules=["No smoking", "Keep quiet"],
        imagePrompt=None
    )
    
    # Use patch instead of monkeypatch.context
    with patch('app.utils.json_service.JSONService.parse_and_validate_json_response', 
              return_value=location_obj):
        
        # Call the method
        result = await location_generator.generate_location(test_world)
    
    # Assertions
    assert isinstance(result, Location)
    assert result.id == "loc123"
    assert result.name == "Test Location"
    assert result.imagePrompt == image_prompt
    
    # Verify expected calls
    assert mock_llm_service.extract_content.call_count == 3 