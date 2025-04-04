import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.game_engine.tools.world_generator import WorldGenerator
from app.schemas.world_generation import World, WorldInput
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
def world_generator(mock_llm_service: MagicMock) -> WorldGenerator:
    """Create a WorldGenerator instance with a mock LLM service."""
    return WorldGenerator(llm_service=mock_llm_service)


@pytest.fixture
def test_world_input() -> WorldInput:
    """Create a test world input."""
    return WorldInput(
        theme="Fantasy",
        genre="Adventure",
        year=1200,  # Medieval period as an integer year
        setting="Kingdom"
    )


class TestWorldGenerator:
    """Test cases for the WorldGenerator class."""
    
    @pytest.mark.asyncio
    async def test_generate_world(
        self,
        world_generator: WorldGenerator,
        test_world_input: WorldInput,
        mock_llm_service: MagicMock
    ):
        """Test the generate_world method."""
        # Mock the LLM service responses
        world_description = "This is a detailed fantasy world description."
        world_rules = """
        [
            "Magic requires years of study and only 1% of the population has the aptitude to master it.",
            "The kingdom is divided into five distinct regions, each ruled by a duke who answers to the High King.",
            "Technology is limited to medieval standards, with rare magical artifacts enhancing capabilities.",
            "Dragons exist but are extremely rare, with fewer than ten known to be alive in the entire realm.",
            "The boundary between the mortal realm and the spirit world weakens during the winter solstice."
        ]
        """
        
        # Configure the mock for extract_content
        mock_llm_service.extract_content.side_effect = [
            world_description,
            world_rules
        ]
        
        # Mock the JSONService.parse_and_validate_string_list
        rules_list = [
            "Magic requires years of study and only 1% of the population has the aptitude to master it.",
            "The kingdom is divided into five distinct regions, each ruled by a duke who answers to the High King.",
            "Technology is limited to medieval standards, with rare magical artifacts enhancing capabilities.",
            "Dragons exist but are extremely rare, with fewer than ten known to be alive in the entire realm.",
            "The boundary between the mortal realm and the spirit world weakens during the winter solstice."
        ]
        
        # Use patch instead of monkeypatch.context
        with patch('app.utils.json_service.JSONService.parse_and_validate_string_list', 
                  return_value=rules_list):
            
            # Call the method
            result = await world_generator.generate_world(test_world_input)
        
        # Assertions
        assert isinstance(result, World)
        assert result.description == world_description
        assert len(result.rules) == 5
        assert result.rules[0] == rules_list[0]
        
        # Verify expected calls
        assert mock_llm_service.extract_content.call_count == 2
        assert mock_llm_service.generate_completion.call_count == 2
    