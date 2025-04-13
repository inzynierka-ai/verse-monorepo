import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.game_engine.tools.story_generator import StoryGenerator
from app.schemas.story_generation import Story, StoryInput
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
def story_generator(mock_llm_service: MagicMock) -> StoryGenerator:
    """Create a StoryGenerator instance with a mock LLM service."""
    return StoryGenerator(llm_service=mock_llm_service)


@pytest.fixture
def test_story_input() -> StoryInput:
    """Create a test story input."""
    return StoryInput(
        theme="Fantasy",
        genre="Adventure",
        year=1200,  # Medieval period as an integer year
        setting="Kingdom"
    )


class TestStoryGenerator:
    """Test cases for the StoryGenerator class."""
    
    @pytest.mark.asyncio
    async def test_generate_story(
        self,
        story_generator: StoryGenerator,
        test_story_input: StoryInput,
        mock_llm_service: MagicMock
    ):
        """Test the generate_story method."""
        # Mock the LLM service responses
        story_description = "This is a detailed fantasy story description."
        story_rules = """
        [
            "Magic requires years of study and only 1% of the population has the aptitude to master it.",
            "The kingdom is divided into five distinct regions, each ruled by a duke who answers to the High King.",
            "Technology is limited to medieval standards, with rare magical artifacts enhancing capabilities.",
            "Dragons exist but are extremely rare, with fewer than ten known to be alive in the entire realm.",
            "The boundary between the mortal realm and the spirit story weakens during the winter solstice."
        ]
        """
        
        # Configure the mock for extract_content
        mock_llm_service.extract_content.side_effect = [
            story_description,
            story_rules
        ]
        
        # Mock the JSONService.parse_and_validate_string_list
        rules_list = [
            "Magic requires years of study and only 1% of the population has the aptitude to master it.",
            "The kingdom is divided into five distinct regions, each ruled by a duke who answers to the High King.",
            "Technology is limited to medieval standards, with rare magical artifacts enhancing capabilities.",
            "Dragons exist but are extremely rare, with fewer than ten known to be alive in the entire realm.",
            "The boundary between the mortal realm and the spirit story weakens during the winter solstice."
        ]
        
        # Use patch instead of monkeypatch.context
        with patch('app.utils.json_service.JSONService.parse_and_validate_string_list', 
                  return_value=rules_list):
            
            # Call the method
            result = await story_generator.generate_story(test_story_input)
        
        # Assertions
        assert isinstance(result, Story)
        assert result.description == story_description
        assert len(result.rules) == 5
        assert result.rules[0] == rules_list[0]
        
        # Verify expected calls
        assert mock_llm_service.extract_content.call_count == 2
        assert mock_llm_service.generate_completion.call_count == 2
    