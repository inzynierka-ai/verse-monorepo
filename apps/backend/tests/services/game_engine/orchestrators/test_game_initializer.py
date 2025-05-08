import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.game_engine.orchestrators.game_initializer import GameInitializer, InitialGameState
from app.services.game_engine.tools.story_generator import StoryGenerator
from app.services.game_engine.tools.character_generator import CharacterGenerator
from app.schemas.story_generation import (
    StoryGenerationInput,
    StoryInput,
    CharacterDraft,
    Story,
    Character
)


@pytest.fixture
def mock_story_generator():
    """Create a mock StoryGenerator for testing."""
    story_generator = MagicMock(spec=StoryGenerator)
    story_generator.generate_story = AsyncMock()
    return story_generator


@pytest.fixture
def mock_character_generator():
    """Create a mock CharacterGenerator for testing."""
    character_generator = MagicMock(spec=CharacterGenerator)
    character_generator.generate_character = AsyncMock()
    return character_generator


@pytest.fixture
def sample_story_input() -> StoryInput:
    """Create a sample story input for testing."""
    return StoryInput(
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
def sample_story_generation_input(sample_story_input: StoryInput, sample_character_draft: CharacterDraft) -> StoryGenerationInput:
    """Create a sample story generation input for testing."""
    return StoryGenerationInput(
        story=sample_story_input,
        playerCharacter=sample_character_draft
    )


@pytest.fixture
def sample_story() -> Story:
    """Create a sample story for testing."""
    return Story(
        description="A story devastated by climate change...",
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
        image_dir="https://localhost:8000/media/comfyui/test.png",
        role="player",
        uuid="12345678-1234-5678-1234-567812345678"
    )


class TestGameInitializer:
    
    @pytest.mark.asyncio
    async def test_initialize_game(
        self,
        mock_story_generator: MagicMock,
        mock_character_generator: MagicMock,
        sample_story_generation_input: StoryGenerationInput,
        sample_story: Story,
        sample_character: Character
    ):
        """Test the initialize_game method with mocked dependencies."""
        # Setup mocks
        mock_story_generator.generate_story.return_value = sample_story
        mock_character_generator.generate_character.return_value = sample_character
        
        # Create initializer with mocks
        initializer = GameInitializer(
            story_generator=mock_story_generator,
            character_generator=mock_character_generator
        )
        
        # Call the initialize_game method
        result = await initializer.initialize_game(sample_story_generation_input)
        
        # Check that the result is correct
        assert isinstance(result, InitialGameState)
        assert result.story == sample_story
        assert result.playerCharacter == sample_character
        
        # Verify the generator methods were called correctly
        mock_story_generator.generate_story.assert_called_once_with(sample_story_generation_input.story)
        mock_character_generator.generate_character.assert_called_once_with(
            sample_story_generation_input.playerCharacter,
            sample_story,
            is_player=True
        )