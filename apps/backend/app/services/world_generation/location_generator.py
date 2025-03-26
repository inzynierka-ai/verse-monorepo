from typing import Optional
from app.services.llm import LLMService, ModelName
from app.schemas.world_generation import (
    Location,
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


async def describe_location(
    world: World,
    llm_service: Optional[LLMService] = None
) -> str:
    """
    Generate a detailed narrative description of a location based on world description.

    Args:
        world: World object containing description and other details
        llm_service: Optional LLMService instance to use

    Returns:
        A detailed narrative description of a single location
    """

    llm_service = llm_service or LLMService()

    user_prompt = create_location_prompt(world)

    messages = [
        llm_service.create_message("system", LOCATION_GENERATOR_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]

    return await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_25_PRO,
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
        llm_service.create_message(
            "system", LOCATION_IMAGE_PROMPT_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]

    return await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_25_PRO,
        temperature=0.7,
        stream=False
    )


async def create_location_json(
    world: World,
    llm_service: Optional[LLMService] = None
) -> Location:
    """
    Generate a detailed location profile based on world description.

    Args:
        world: World object containing description and other details
        llm_service: Optional LLMService instance to use

    Returns:
        Location object containing detailed location profile
    """

    llm_service = llm_service or LLMService()

    location_description = await describe_location(world, llm_service)

    user_prompt = CREATE_LOCATION_JSON_USER_PROMPT_TEMPLATE.format(
        location_descriptions=location_description
    )

    messages = [
        llm_service.create_message(
            "system", CREATE_LOCATION_JSON_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]

    response = await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_25_PRO,
        temperature=0.7,
        stream=False
    )

    try:
        # Parse the JSON response into a list with a single location
        location = JSONService.parse_and_validate_json_response(
            response, Location)

        if not location:
            raise ValueError("No location data found in response")

        # Generate image prompt for the location
        image_prompt = await generate_image_prompt(location, world.description, llm_service)
        location.imagePrompt = image_prompt

        return location
    except Exception as e:
        raise ValueError(
            f"Failed to parse location data: {str(e)}, raw response: {response}")


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
