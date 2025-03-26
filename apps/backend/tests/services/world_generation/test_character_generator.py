import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.world_generation.character_generator import CharacterGenerator
from app.schemas.world_generation import CharacterDraft, World, CharacterFromLLM
from app.services.llm import LLMService


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service for testing."""
    llm_service = MagicMock(spec=LLMService)
    llm_service.create_message = MagicMock(return_value={"role": "user", "content": "test"})
    llm_service.generate_completion = AsyncMock()
    return llm_service


@pytest.fixture
def character_generator(mock_llm_service: LLMService):
    """Create a CharacterGenerator instance with a mock LLM service."""
    return CharacterGenerator(llm_service=mock_llm_service)


@pytest.fixture
def test_character_draft():
    """Create a test character draft."""
    return CharacterDraft(
        name="Test Character",
        age=30,
        appearance="Tall with brown hair",
        background="A mysterious background",
    )


@pytest.fixture
def test_world():
    """Create a test world."""
    return World(
        description="A test world description",
        rules=["Rule 1", "Rule 2"],
        prolog="Once upon a time...",
    )



@pytest.mark.asyncio
async def test_generate_character(
    character_generator: CharacterGenerator, 
    test_character_draft: CharacterDraft, 
    test_world: World, 
    mock_llm_service: MagicMock
):
    """Test the generate_character method."""
    # Mock the LLM service responses
    character_description = "This is a detailed character description."
    character_json = """
    {
        "id": "char123",
        "name": "Test Character",
        "role": "npc",
        "description": "Tall with brown hair and a distinguished look",
        "personalityTraits": ["Brave", "Intelligent"],
        "backstory": "A mysterious background with many secrets",
        "goals": ["Find the truth", "Protect their family"],
        "relationships": [
            {
                "id": "char456",
                "level": 5,
                "type": "friend",
                "backstory": "Old childhood friends"
            }
        ],
        "connectedLocations": ["loc123"]
    }
    """
    image_prompt = "A detailed image of Test Character standing tall with brown hair."
    
    # Configure the mock
    mock_llm_service.generate_completion.side_effect = [
        character_description,  # _describe_character
        character_json,         # _create_character_json
        image_prompt,           # _generate_image_prompt
    ]
    
    # Call the method
    result = await character_generator.generate_character(test_character_draft, test_world, is_player=False)
    
    
    # Assertions
    assert isinstance(result, CharacterFromLLM)
    assert result.imagePrompt == image_prompt
    
    # Verify expected calls
    assert mock_llm_service.generate_completion.call_count == 3
