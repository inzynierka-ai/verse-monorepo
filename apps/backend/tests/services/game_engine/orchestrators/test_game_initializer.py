import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.game_engine.orchestrators.game_initializer import GameInitializer, InitialGameState
from app.services.game_engine.tools.world_generator import WorldGenerator
from app.services.game_engine.tools.character_generator import CharacterGenerator
from app.schemas.world_generation import (
    WorldGenerationInput,
    WorldInput,
    CharacterDraft,
    World,
    Character
)


@pytest.fixture
def mock_world_generator():
    """Create a mock WorldGenerator for testing."""
    world_generator = MagicMock(spec=WorldGenerator)
    world_generator.generate_world = AsyncMock()
    return world_generator


@pytest.fixture
def mock_character_generator():
    """Create a mock CharacterGenerator for testing."""
    character_generator = MagicMock(spec=CharacterGenerator)
    character_generator.generate_character = AsyncMock()
    return character_generator


@pytest.fixture
def sample_world_input() -> WorldInput:
    """Create a sample world input for testing."""
    return WorldInput(
        theme="survival",
        genre="post-apocalyptic",
        year=2050,
        setting="abandoned city"
    )


@pytest.fixture
def sample_character_draft() -> CharacterDraft:
    """Create a sample character draft for testing."""
    return CharacterDraft(
        name="Alex",
        age=28,
        appearance="Tall with dark hair and a scar on the left cheek",
        background="Former engineer turned scavenger"
    )


@pytest.fixture
def sample_world_generation_input(sample_world_input: WorldInput, sample_character_draft: CharacterDraft) -> WorldGenerationInput:
    """Create a sample world generation input for testing."""
    return WorldGenerationInput(
        world=sample_world_input,
        playerCharacter=sample_character_draft
    )


@pytest.fixture
def sample_world() -> World:
    """Create a sample world for testing."""
    return World(
        description="A world devastated by climate change...",
        rules=["Resources are scarce", "Technology is fragmented"]
    )


@pytest.fixture
def sample_character() -> Character:
    """Create a sample character for testing."""
    return Character(
        name="Alex",
        description="A resourceful survivor with engineering skills",
        personalityTraits=["Resourceful", "Cautious", "Determined"],
        backstory="Once a promising engineer, now searching for purpose",
        goals=["Find clean water source", "Build a safe community"],
        relationships=[],
        imagePrompt="A tall person with dark hair and scar, wearing practical clothing",
        role="player"
    )


class TestGameInitializer:
    
    @pytest.mark.asyncio
    async def test_initialize_game(
        self,
        mock_world_generator: MagicMock,
        mock_character_generator: MagicMock,
        sample_world_generation_input: WorldGenerationInput,
        sample_world: World,
        sample_character: Character
    ):
        """Test the initialize_game method with mocked dependencies."""
        # Setup mocks
        mock_world_generator.generate_world.return_value = sample_world
        mock_character_generator.generate_character.return_value = sample_character
        
        # Create initializer with mocks
        initializer = GameInitializer(
            world_generator=mock_world_generator,
            character_generator=mock_character_generator
        )
        
        # Call the initialize_game method
        result = await initializer.initialize_game(sample_world_generation_input)
        
        # Check that the result is correct
        assert isinstance(result, InitialGameState)
        assert result.world == sample_world
        assert result.playerCharacter == sample_character
        
        # Verify the generator methods were called correctly
        mock_world_generator.generate_world.assert_called_once_with(sample_world_generation_input.world)
        mock_character_generator.generate_character.assert_called_once_with(
            sample_world_generation_input.playerCharacter,
            sample_world,
            is_player=True
        )