import logging
from typing import Optional
from app.services.llm import LLMService, ModelName
from app.schemas.world_generation import (
    CharacterFromLLM,
    World,
    Character,
    CharacterDraft
)
from app.prompts import (
    CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE,
    DESCRIBE_CHARACTER_SYSTEM_PROMPT,
    CREATE_CHARACTER_JSON_SYSTEM_PROMPT,
    CREATE_CHARACTER_JSON_USER_PROMPT_TEMPLATE,
    CHARACTER_IMAGE_PROMPT_SYSTEM_PROMPT,
    CHARACTER_IMAGE_PROMPT_USER_TEMPLATE
)
from app.utils.json_service import JSONService
from app.services.image_generation.comfyui_service import ComfyUIService
from app.core.config import settings


class CharacterGenerator:
    """
    Service for generating characters.        
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()

    async def generate_character(self, character_draft: CharacterDraft, world: World, is_player: bool) -> Character:
        """
        Orchestrates the entire character generation process.

        Args:
            character_draft: Character draft to be used for character generation
            world: World object containing description and other details

        Returns:
            Fully generated Character object with description and image prompt
        """
        # 1. Generate detailed character description
        character_description = await self._describe_character(character_draft, world)
        # 2. Create character JSON from description
        character_from_llm = await self._create_character_json(character_description)
        # 3. Generate image prompt for the character
        image_prompt = await self._generate_image_prompt(character_from_llm, world.description)
        # 4. Generate image for the character
        image_url = await self._generate_image(image_prompt)

        # Create Character object from CharacterFromLLM
        character = Character(
            **character_from_llm.model_dump(),
            imageUrl=image_url,
            role="player" if is_player else "npc"
        )

        return character

    async def _describe_character(
        self,
        character: CharacterDraft,
        world: World
    ) -> str:
        """
        Generate a detailed narrative description of a character based on character draft and world description.

        Args:
            character: Character draft to be used for character generation
            world: World object containing description and other details

        Returns:
            A detailed narrative description of a single character
        """
        user_prompt = self._create_character_prompt(character, world)

        messages = [
            self.llm_service.create_message("system", DESCRIBE_CHARACTER_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_25_PRO,
            temperature=0.7,
            stream=False
        )

        return await self.llm_service.extract_content(response)

    async def _generate_image(self, image_prompt: str) -> str:
        """
        Generate an image for a character.
        """
        import asyncio
        
        comfyui_service = ComfyUIService()
        logging.info(f"Generating image for prompt: {image_prompt}")
        
        # Run the synchronous generate_image method in a thread pool
        loop = asyncio.get_event_loop()
        result_dict = await loop.run_in_executor(
            None, 
            lambda: comfyui_service.generate_image(image_prompt, "character")
        )
        
        logging.info(f"Generated image: {result_dict}")
        return f"{settings.BACKEND_URL}{result_dict['imagePath']}"

    async def _generate_image_prompt(
        self,
        character: CharacterFromLLM,
        world_description: str
    ) -> str:
        """
        Generate a detailed image prompt for a character.

        Args:
            character: The detailed character to generate an image prompt for
            world_description: The world description for context

        Returns:
            A detailed image prompt for the character
        """
        user_prompt = CHARACTER_IMAGE_PROMPT_USER_TEMPLATE.format(
            character_name=character.name,
            character_description=character.description,
            world_description=world_description
        )

        messages = [
            self.llm_service.create_message("system", CHARACTER_IMAGE_PROMPT_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_25_PRO,
            temperature=0.7,
            stream=False
        )

        return await self.llm_service.extract_content(response)

    async def _create_character_json(
        self,
        character_description: str
    ) -> CharacterFromLLM:
        """
        Generate a detailed character profile based on character description.

        Args:
            character_description: Detailed character description

        Returns:
            Character object containing detailed character profile
        """
        user_prompt = CREATE_CHARACTER_JSON_USER_PROMPT_TEMPLATE.format(
            character_descriptions=character_description
        )

        messages = [
            self.llm_service.create_message("system", CREATE_CHARACTER_JSON_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_FLASH_LITE,
            temperature=0.7,
            stream=False
        )

        response_text = await self.llm_service.extract_content(response)

        try:
            # Parse the JSON response into a character object
            character = JSONService.parse_and_validate_json_response(
                response_text, CharacterFromLLM)

            if not character:
                raise ValueError("No character data found in response")

            return character
        except Exception as e:
            raise ValueError(
                f"Failed to parse character data: {str(e)}, raw response: {response_text}") from e

    def _create_character_prompt(
        self,
        character: CharacterDraft,
        world: World
    ) -> str:
        """
        Create a formatted prompt for character generation.

        Args:
            character: The character draft to be used for character generation
            world: The world description

        Returns:
            Formatted prompt string
        """
        return CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE.format(
            character_draft=character,
            world_description=world.description,
            world_rules=world.rules
        )
