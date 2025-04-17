import logging
import uuid
from typing import Optional
from sqlalchemy.orm import Session
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
from sqlalchemy.orm import Session
from app.models.location import Location as LocationModel

class LocationGenerator:
    """
    Service for generating locations.
    """
    def __init__(self, llm_service: Optional[LLMService] = None, db_session: Optional[Session] = None):
        self.llm_service = llm_service or LLMService()
        self.db_session = db_session
    
    async def generate_location(self, story: Story, description: str = "") -> Location:
        """
        Generate a complete location.

        Args:
            story: Story object containing description and other details
            description: Optional description to guide location generation

        Returns:
            Location object containing location details and image URL
        """
        # 1. Generate UUID first - we need it for the entire process
        location_uuid = str(uuid.uuid4())
        
        # 2. Generate detailed location description
        location_description = await self._describe_location(story, description, location_uuid)
        
        # 3. Create location JSON from description
        location_from_llm = await self._create_location_json(location_description, location_uuid)

        # 4. Generate image prompt for the location
        image_prompt = await self._generate_image_prompt(location_from_llm, story.description, location_uuid)

        # 5. Generate image for the location
        image_url = await self._generate_image(image_prompt)
        
        # 6. Create the final location with image URL and UUID
        location = Location(
            **location_from_llm.model_dump(),
            imageUrl=image_url,
            uuid=location_uuid
        )
        
        # 7. Save to database as a side effect
        if story.id is not None and self.db_session is not None:
            await self._save_location_to_db(location, story.id, image_prompt)
        else:
            logging.warning("Story ID is None or no database session, skipping database save")
        
        # 8. Return the Pydantic Location object
        return location

    
    async def _describe_location(self, story: Story, description: str, location_uuid: str) -> str:
        """
        Generate a detailed narrative description of a location based on story description.

        Args:
            story: Story object containing description and other details
            description: Optional description to guide location generation
            location_uuid: Unique identifier for the location

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
            stream=False,
            metadata={
                "location_uuid": location_uuid
            }
        )

        return await self.llm_service.extract_content(response)

    async def _generate_image_prompt(
        self,
        location: LocationFromLLM,
        story_description: str,
        location_uuid: str
    ) -> str:
        """
        Generate a detailed image prompt for a location.

        Args:
            location: The detailed location to generate an image prompt for
            story_description: The story description for context
            location_uuid: Unique identifier for the location

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
            stream=False,
            metadata={
                "location_uuid": location_uuid
            }
        )

        return await self.llm_service.extract_content(response)

    async def _generate_image(self, image_prompt: str) -> str:
        """
        Generate an image for a location.
        """
        import asyncio
        
        comfyui_service = ComfyUIService()
        logging.info(f"Generating image for prompt: {image_prompt}")
        
        # Run the synchronous generate_image method in a thread pool
        loop = asyncio.get_event_loop()
        result_dict = await loop.run_in_executor(
            None, 
            lambda: comfyui_service.generate_image(image_prompt, "location")
        )
        
        logging.info(f"Generated image: {result_dict}")
        return f"{settings.BACKEND_URL}{result_dict['imagePath']}"
    
    async def _create_location_json(
        self,
        location_description: str,
        location_uuid: str
    ) -> LocationFromLLM:
        """
        Generate a detailed location profile based on location description.

        Args:
            location_description: Detailed location description
            location_uuid: Unique identifier for the location

        Returns:
            Location object containing detailed location profile
        """
        user_prompt = CREATE_LOCATION_JSON_USER_PROMPT_TEMPLATE.format(
            location_description=location_description
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
            stream=False,
            metadata={
                "location_uuid": location_uuid
            }
        )
        
        response_text = await self.llm_service.extract_content(response)

        try:
            # Parse the JSON response into a location object
            location = JSONService.parse_and_validate_json_response(
                response_text, LocationFromLLM)

            if not location:
                raise ValueError("No location data found in response")

            return location
        except Exception as e:
            raise ValueError(
                f"Failed to parse location data: {str(e)}, raw response: {response_text}") from e

    async def _save_location_to_db(self, location: Location, story_id: int, image_prompt: str) -> LocationModel:
        """
        Save the generated location to the database.
        
        Args:
            location: The generated location object with UUID already set
            story_id: ID of the story to associate with
            image_prompt: The image prompt used to generate the location image
            
        Returns:
            The saved database model
        """
        try:
            # Create a database model from the location schema
            db_location = LocationModel(
                name=location.name,
                description=location.description,
                rules=", ".join(location.rules) if hasattr(location, 'rules') and location.rules else "",
                image_dir=location.imageUrl,
                image_prompt=image_prompt,
                story_id=story_id,
                uuid=location.uuid
            )
            
            # Add to database session if available
            if self.db_session is not None:
                self.db_session.add(db_location)
                self.db_session.commit()
                logging.info(f"Location {location.name} saved to database with ID {db_location.id}")
                return db_location
            else:
                logging.warning("No database session available, location not saved to database")
                return db_location
        except Exception as e:
            logging.exception(f"Failed to save location to database: {str(e)}")
            # Don't raise the exception, just log it, to avoid breaking the game flow
            if self.db_session is not None and hasattr(self.db_session, 'is_active') and self.db_session.is_active:
                self.db_session.rollback()
            raise

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
