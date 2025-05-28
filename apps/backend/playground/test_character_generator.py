import asyncio
from app.services.characters.character_generator import CharacterGenerator
from app.schemas.story_generation import Story, CharacterDraft
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.schemas.story_generation import Story, CharacterDraft, Character, CharacterFromLLM
from app.services.llm import LLMService

async def test_character_brief_description():
    # Create test data
    # Fixture for story
    @pytest.fixture
    def test_story():
        return Story(
            id=None,
            description="A medieval fantasy world with magic",
            rules="Magic is rare but powerful"
        )

    # Fixture for character draft
    @pytest.fixture
    def test_character_draft():
        return CharacterDraft(
            name="Elara",
            concept="A mysterious forest healer"
        )

    # Fixture for mocked LLM service
    @pytest.fixture
    def mock_llm_service():
        mock_service = AsyncMock(spec=LLMService)
        
        # Set up extract_content to return appropriate test data
        async def mock_extract_content(response):
            if "character_draft" in str(response):
                return '{"name": "Elara", "concept": "A mysterious forest healer"}'
            elif "describe_character" in str(response):
                return "Elara is a mysterious healer who lives in the ancient forest."
            elif "character_json" in str(response):
                return '{"name": "Elara", "description": "Elara is a mysterious healer who lives in the ancient forest.", "brief_description": "A mysterious forest healer with deep knowledge of herbal remedies.", "backstory": "Orphaned at a young age", "goals": ["Find rare herbs", "Help villagers"], "personalityTraits": ["Kind", "Mysterious"]}'
            elif "image_prompt" in str(response):
                return "A young woman with flowing green robes standing in a magical forest, herbs and potions at her side."
            return ""
        
        mock_service.extract_content.side_effect = mock_extract_content
        mock_service.create_message.return_value = {"role": "user", "content": "test"}
        mock_service.generate_completion = AsyncMock()
        
        return mock_service

    # Test create_character_draft_from_description
    @pytest.mark.asyncio
    async def test_create_character_draft_from_description(test_story, mock_llm_service):
        generator = CharacterGenerator(llm_service=mock_llm_service)
        
        character_draft = await generator.create_character_draft_from_description(
            "A wise old wizard", test_story
        )
        
        assert mock_llm_service.generate_completion.called
        assert character_draft.name == "Elara"
        assert character_draft.concept == "A mysterious forest healer"

    # Test generate_character with mocked components
    @pytest.mark.asyncio
    async def test_generate_character_with_mocks(test_story, test_character_draft, mock_llm_service):
        generator = CharacterGenerator(llm_service=mock_llm_service)
        
        # Mock internal methods to isolate the test
        generator._generate_image = AsyncMock(return_value="http://example.com/image.jpg")
        generator._save_character_to_db = AsyncMock()
        
        character = await generator.generate_character(
            test_character_draft, test_story, is_player=True
        )
        
        assert character.name == "Elara"
        assert character.role == "player"
        assert character.image_dir == "http://example.com/image.jpg"
        assert len(character.description) > 0
        assert len(character.brief_description) > 0

    # Test generate_character_from_description
    @pytest.mark.asyncio
    async def test_generate_character_from_description(test_story, mock_llm_service):
        generator = CharacterGenerator(llm_service=mock_llm_service)
        
        # Mock internal methods
        generator.create_character_draft_from_description = AsyncMock(
            return_value=CharacterDraft(name="Elara", concept="A mysterious forest healer")
        )
        generator.generate_character = AsyncMock(
            return_value=Character(
                name="Elara", 
                description="A detailed description", 
                brief_description="A brief description",
                backstory="Orphaned at a young age",
                goals=["Find rare herbs"],
                image_dir="http://example.com/image.jpg",
                role="npc",
                uuid="test-uuid"
            )
        )
        
        character = await generator.generate_character_from_description(
            "A healer from the woods", test_story, is_player=False
        )
        
        assert generator.create_character_draft_from_description.called
        assert generator.generate_character.called
        assert character.name == "Elara"
        assert character.role == "npc"

    # Test image prompt generation
    @pytest.mark.asyncio
    async def test_generate_image_prompt(mock_llm_service):
        generator = CharacterGenerator(llm_service=mock_llm_service)
        
        character = CharacterFromLLM(
            name="Elara",
            description="Elara is a mysterious healer who lives in the ancient forest.",
            brief_description="A mysterious forest healer",
            backstory="Orphaned at a young age",
            goals=["Find rare herbs"],
            personalityTraits=["Kind", "Mysterious"]
        )
        
        prompt = await generator._generate_image_prompt(
            character, "A medieval fantasy world", "test-uuid"
        )
        
        assert mock_llm_service.generate_completion.called
        assert "flowing green robes" in prompt
        assert "magical forest" in prompt

    # Original test from the file for reference
    async def test_character_brief_description():
        # Create test data
        story = Story(
            id=None,  # No need to save to DB for testing
            description="A medieval fantasy world with magic",
            rules="Magic is rare but powerful"
        )
        
        character_draft = CharacterDraft(
            name="Elara",
            concept="A mysterious forest healer"
        )
        
        # Initialize the generator
        generator = CharacterGenerator()
        
        # Generate character
        character = await generator.generate_character(character_draft, story, is_player=True)
        
        # Print results to verify
        print(f"Character name: {character.name}")
        print(f"Brief description: {character.brief_description}")
        print(f"Full description length: {len(character.description)} characters")
        
        return character

    if __name__ == "__main__":
        character = asyncio.run(test_character_brief_description())