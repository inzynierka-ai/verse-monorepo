from typing import Optional
from app.services.llm import LLMService, ModelName
from app.schemas.world_generation import (
    Location,
    LocationFromLLM,
    World
)
from app.prompts.location_generator import (
    LOCATION_GENERATOR_SYSTEM_PROMPT,
    LOCATION_GENERATOR_USER_PROMPT_TEMPLATE,
    LOCATION_IMAGE_PROMPT_SYSTEM_PROMPT,
    LOCATION_IMAGE_PROMPT_USER_TEMPLATE,
    CREATE_LOCATION_JSON_SYSTEM_PROMPT,
    CREATE_LOCATION_JSON_USER_PROMPT_TEMPLATE
)
from app.utils.json_service import JSONService


class LocationGenerator:
    """
    Service for generating locations.
    """
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
    
    async def generate_location(self, world: World) -> Location:
        """
        Orchestrates the entire location generation process.
        
        Args:
            world: World object containing description and other details
            
        Returns:
            Fully generated Location object with description and image prompt
        """
        # 1. Generate detailed location description
        location_description = await self._describe_location(world)
        # 2. Create location JSON from description
        location_from_llm = await self._create_location_json(location_description)

        image_prompt = await self._generate_image_prompt(location_from_llm, world.description)

        location = Location(
            **location_from_llm.model_dump(),
            imagePrompt=image_prompt
        )
        
        return location

    
    async def _describe_location(self, world: World) -> str:
        """
        Generate a detailed narrative description of a location based on world description.

        Args:
            world: World object containing description and other details

        Returns:
            A detailed narrative description of a single location
        """
        user_prompt = self._create_location_prompt(world)

        messages = [
            self.llm_service.create_message("system", LOCATION_GENERATOR_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_25_PRO,
            temperature=0.7,
            stream=False
        )

        return await self.llm_service.extract_content(response)

    async def _generate_image_prompt(
        self,
        location: LocationFromLLM,
        world_description: str
    ) -> str:
        """
        Generate a detailed image prompt for a location.

        Args:
            location: The detailed location to generate an image prompt for
            world_description: The world description for context

        Returns:
            A detailed image prompt for the location
        """
        user_prompt = LOCATION_IMAGE_PROMPT_USER_TEMPLATE.format(
            location_name=location.name,
            location_description=location.description,
            world_description=world_description
        )

        messages = [
            self.llm_service.create_message(
                "system", LOCATION_IMAGE_PROMPT_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_25_PRO,
            temperature=0.7,
            stream=False
        )

        return await self.llm_service.extract_content(response)

    async def _create_location_json(
        self,
        location_description: str,
    ) -> LocationFromLLM:
        """
        Generate a detailed location profile based on location description.

        Args:
            location_description: Detailed location description
            

        Returns:
            Location object containing detailed location profile
        """
        user_prompt = CREATE_LOCATION_JSON_USER_PROMPT_TEMPLATE.format(
            location_description=location_description,
            
        )

        messages = [
            self.llm_service.create_message(
                "system", CREATE_LOCATION_JSON_SYSTEM_PROMPT),
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
            # Parse the JSON response into a location object
            location = JSONService.parse_and_validate_json_response(
                response_text, Location)

            if not location:
                raise ValueError("No location data found in response")

            # Generate image prompt for the location
            

            return location
        except Exception as e:
            raise ValueError(
                f"Failed to parse location data: {str(e)}, raw response: {response_text}") from e

    def _create_location_prompt(self, world: World) -> str:
        """
        Create a formatted prompt for location generation.

        Args:
            world: World object containing description and other details

        Returns:
            Formatted prompt string
        """
        return LOCATION_GENERATOR_USER_PROMPT_TEMPLATE.format(
            world_description=world.description,
            world_rules=world.rules,
            world_prolog=world.prolog
        )
