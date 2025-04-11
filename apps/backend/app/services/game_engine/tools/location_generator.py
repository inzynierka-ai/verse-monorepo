from typing import Optional
from app.services.llm import LLMService, ModelName
from app.schemas.story_generation import (
    Location,
    LocationFromLLM,
    Story
)
from app.prompts.location_generator import (
    LOCATION_GENERATOR_SYSTEM_PROMPT,
    LOCATION_GENERATOR_USER_PROMPT_TEMPLATE,
    LOCATION_IMAGE_PROMPT_SYSTEM_PROMPT,
    LOCATION_IMAGE_PROMPT_USER_TEMPLATE,
    CREATE_LOCATION_JSON_SYSTEM_PROMPT,
    CREATE_LOCATION_JSON_USER_PROMPT_TEMPLATE,
)
from app.utils.json_service import JSONService
from app.services.image_generation.comfyui_service import ComfyUIService
from app.core.config import settings

class LocationGenerator:
    """
    Service for generating locations.
    """
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
    
    async def generate_location(self, story: Story, description: str) -> Location:
        """
        Generate a complete location.

        Args:
            story: Story object containing description and other details
            description: Optional description to guide location generation

        Returns:
            Location object containing location details and image URL
        """
        # 1. Generate detailed location description
        location_description = await self._describe_location(story, description)
        # 2. Create location JSON from description
        location_from_llm = await self._create_location_json(location_description)

        image_prompt = await self._generate_image_prompt(location_from_llm, story.description)

        image_url = await self._generate_image(image_prompt)
        
        # Create the final location with image URL
        location = Location(
            **location_from_llm.model_dump(),
            imageUrl=image_url
        )
        
        return location

    
    async def _describe_location(self, story: Story, description: str) -> str:
        """
        Generate a detailed narrative description of a location based on story description.

        Args:
            story: Story object containing description and other details
            description: Optional description to guide location generation

        Returns:
            A detailed narrative description of a single location
        """
        user_prompt = self._create_location_prompt(story, description)

        messages = [
            self.llm_service.create_message("system", LOCATION_GENERATOR_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GPT4O_MINI,
            temperature=0.7,
            stream=False
        )

        return await self.llm_service.extract_content(response)

    async def _generate_image_prompt(
        self,
        location: LocationFromLLM,
        story_description: str
    ) -> str:
        """
        Generate a detailed image prompt for a location.

        Args:
            location: The detailed location to generate an image prompt for
            story_description: The story description for context

        Returns:
            A detailed image prompt for the location
        """
        user_prompt = LOCATION_IMAGE_PROMPT_USER_TEMPLATE.format(
            location_name=location.name,
            location_description=location.description,
            story_description=story_description
        )

        messages = [
            self.llm_service.create_message(
                "system", LOCATION_IMAGE_PROMPT_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GPT4O_MINI,
            temperature=0.7,
            stream=False
        )

        return await self.llm_service.extract_content(response)

    async def _generate_image(self, image_prompt: str) -> str:
        """
        Generate an image for a character.
        """

        comfyui_service = ComfyUIService()
        result = comfyui_service.generate_image(image_prompt, "location")
        return f"{settings.BACKEND_URL}{result['imagePath']}"
    
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
            model=ModelName.GPT4O_MINI,
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

    def _create_location_prompt(self, story: Story, description: str) -> str:
        """
        Create a formatted prompt for location generation.

        Args:
            story: Story object containing description and other details
            description: description to guide location generation

        Returns:
            Formatted prompt string
        """
        return LOCATION_GENERATOR_USER_PROMPT_TEMPLATE.format(
            story_description=story.description,
            story_rules=story.rules,
            description=description
        )
