import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.game_engine.tools.character_generator import CharacterGenerator
from app.schemas.story_generation import (
    CharacterDraft, 
    Story, 
    Character, 
    CharacterFromLLM,
    CharacterRelationship
)
from app.services.llm import LLMService


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service for testing."""
    llm_service = MagicMock(spec=LLMService)
    llm_service.create_message = MagicMock(return_value={"role": "user", "content": "test"})
    llm_service.generate_completion = AsyncMock()
    llm_service.extract_content = AsyncMock()
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
def test_story():
    """Create a test story."""
    return Story(
        description="A test story description",
        rules=["Rule 1", "Rule 2"],
    )


@pytest.mark.asyncio
async def test_generate_character(
    character_generator: CharacterGenerator, 
    test_character_draft: CharacterDraft, 
    test_story: Story, 
    mock_llm_service: MagicMock
):
    """Test the generate_character method."""
    # Mock the LLM service responses
    character_description = "This is a detailed character description."
    
    # Create a valid CharacterRelationship object
    relationship = CharacterRelationship(
        name="John Smith",  
        level=5,
        type="friend",
        backstory="Old childhood friends"
    )
    
    # Define a character with valid relationships
    character_from_llm = CharacterFromLLM(
        name="Test Character",
        description="Tall with brown hair and a distinguished look",
        personalityTraits=["Brave", "Intelligent"],
        backstory="A mysterious background with many secrets",
        goals=["Find the truth", "Protect their family"],
        relationships=[relationship]
    )
    
    image_prompt = "A detailed image of Test Character standing tall with brown hair."
    
    # Configure the mock for extract_content
    mock_llm_service.extract_content.side_effect = [
        character_description,
        "dummy_json",  # This will be bypassed with the patch
        image_prompt
    ]
    
    # Configure generate_completion to return something (not used directly)
    mock_llm_service.generate_completion.return_value = "dummy_response"
    
    # Patch JSONService.parse_and_validate_json_response to return our valid character
    with patch('app.utils.json_service.JSONService.parse_and_validate_json_response', 
              return_value=character_from_llm):
        
        # Call the method
        result = await character_generator.generate_character(test_character_draft, test_story, is_player=False)
    
    # Assertions
    assert isinstance(result, Character)
    assert result.name == "Test Character"
    assert len(result.relationships) == 1
    assert result.relationships[0].name == "John Smith"
    
    # Verify expected calls
    assert mock_llm_service.generate_completion.call_count == 3
    assert mock_llm_service.extract_content.call_count == 3
