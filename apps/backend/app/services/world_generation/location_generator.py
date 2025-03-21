from typing import  Optional
from app.services.llm import LLMService, ModelName
from app.schemas.world_generation import (
    Location,
    LocationsOutput,
    World
)
from app.prompts import (
    LOCATION_GENERATOR_SYSTEM_PROMPT,
    LOCATION_GENERATOR_USER_PROMPT_TEMPLATE,
    LOCATION_IMAGE_PROMPT_SYSTEM_PROMPT,
    LOCATION_IMAGE_PROMPT_USER_TEMPLATE,
    CREATE_LOCATION_JSON_SYSTEM_PROMPT,
    CREATE_LOCATION_JSON_USER_PROMPT_TEMPLATE
)
from app.utils.json_service import JSONService
import asyncio


async def describe_locations(
    world: World,
    llm_service: Optional[LLMService] = None
) -> str:
    """
    Generate detailed narrative descriptions of locations based on world description.
    
    Args:
        world: World object containing description and other details
        llm_service: Optional LLMService instance to use
        
    Returns:
        A detailed narrative description of the locations
    """
    
    llm_service = llm_service or LLMService()
    
    user_prompt = create_location_prompt(world)
    
    messages = [
        llm_service.create_message("system", LOCATION_GENERATOR_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]
    
    return await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_PRO,
        temperature=0.7,
        stream=False
    )


async def generate_image_prompt(
    location: Location,
    world_description: str,
    llm_service: Optional[LLMService] = None
) -> str:
    """
    Generate a detailed image prompt for a location.
    
    Args:
        location: The detailed location to generate an image prompt for
        world_description: The world description for context
        llm_service: Optional LLMService instance to use
        
    Returns:
        A detailed image prompt for the location
    """
    llm_service = llm_service or LLMService()
    
    user_prompt = LOCATION_IMAGE_PROMPT_USER_TEMPLATE.format(
        location_name=location.name,
        location_description=location.description,
        world_description=world_description
    )
    
    messages = [
        llm_service.create_message("system", LOCATION_IMAGE_PROMPT_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]
    
    return await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_PRO,
        temperature=0.7,
        stream=False
    )


async def generate_locations(
    world: World,
    llm_service: Optional[LLMService] = None
) -> LocationsOutput:
    """
    Generate detailed location profiles based on world description.
    
    Args:
        world: World object containing description and other details
        llm_service: Optional LLMService instance to use
        
    Returns:
        LocationsOutput containing detailed location profiles
    """
    
    llm_service = llm_service or LLMService()
    
    location_descriptions = await describe_locations(world, llm_service)
    
    user_prompt = CREATE_LOCATION_JSON_USER_PROMPT_TEMPLATE.format(
        location_descriptions=location_descriptions
    )
    
    messages = [
        llm_service.create_message("system", CREATE_LOCATION_JSON_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]
    
    response = await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_PRO,
        temperature=0.7,
        stream=False
    )
    
    try:
        locations_data = JSONService.parse_and_validate_json_list(response, Location)
        
        world_description = world.description
        
        image_prompt_tasks = [
            generate_image_prompt(location, world_description, llm_service)
            for location in locations_data
        ]
        image_prompts = await asyncio.gather(*image_prompt_tasks)

        for location, image_prompt in zip(locations_data, image_prompts):
            location.imagePrompt = image_prompt
        
        return LocationsOutput(locations=locations_data)
    except Exception as e:
        raise ValueError(f"Failed to parse location data: {str(e)}, raw response: {response}")


def create_location_prompt(
    world: World
) -> str:
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