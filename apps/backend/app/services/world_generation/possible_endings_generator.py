from typing import List, Optional

from app.services.llm import LLMService, ModelName
from app.schemas.world_generation import PossibleEnding, PossibleEndingsOutput, Character, Location
from app.utils.json_service import JSONService
from app.prompts import (
    POSSIBLE_ENDINGS_SYSTEM_PROMPT,
    POSSIBLE_ENDINGS_USER_PROMPT_TEMPLATE,
    CREATE_ENDINGS_JSON_SYSTEM_PROMPT,
    CREATE_ENDINGS_JSON_USER_PROMPT_TEMPLATE
)


async def generate_possible_endings(
    chapter_overview: str, 
    characters: List[Character], 
    locations: List[Location],
    llm_service: Optional[LLMService] = None
) -> PossibleEndingsOutput:
    """
    Generate multiple possible endings based on chapter information.
    
    Args:
        chapter_overview: Free-form overview of the chapter
        characters: List of character information
        locations: List of location information
        llm_service: Optional LLMService instance
        
    Returns:
        PossibleEndingsOutput containing the possible endings
    """
    llm_service = llm_service or LLMService()
    
    # Create a prompt for the LLM to generate possible endings
    prompt = create_endings_prompt(chapter_overview, characters, locations)
    
    # Generate free-form endings descriptions
    endings_descriptions = await generate_endings_descriptions(prompt, llm_service)
    
    # Convert free-form descriptions to structured JSON
    endings = await structure_endings_to_json(endings_descriptions, llm_service)
    
    return PossibleEndingsOutput(possibleEndings=endings)


def create_endings_prompt(
    chapter_overview: str, 
    characters: List[Character], 
    locations: List[Location]
) -> str:
    """
    Create a prompt for the LLM to generate possible endings.
    
    Args:
        chapter_overview: Free-form overview of the chapter
        characters: List of character information
        locations: List of location information
        
    Returns:
        Formatted prompt string
    """
    # Extract key character information
    character_info = "\n".join([
        f"- {char.name}: {char.role} - {char.description[:100]}..."
        for char in characters[:5]  # Limit to 5 characters for prompt clarity
    ])
    
    # Extract key location information
    location_info = "\n".join([
        f"- {loc.name}: {loc.description[:100]}..."
        for loc in locations[:5]  # Limit to 5 locations for prompt clarity
    ])
    
    # Construct the prompt using template
    return POSSIBLE_ENDINGS_USER_PROMPT_TEMPLATE.format(
        chapter_overview=chapter_overview,
        character_info=character_info,
        location_info=location_info
    )


async def generate_endings_descriptions(
    prompt: str,
    llm_service: LLMService
) -> str:
    """
    Generate free-form descriptions of possible endings.
    
    Args:
        prompt: The formatted prompt for ending generation
        llm_service: LLMService instance
        
    Returns:
        Free-form descriptions of possible endings
    """
    messages = [
        llm_service.create_message("system", POSSIBLE_ENDINGS_SYSTEM_PROMPT),
        llm_service.create_message("user", prompt)
    ]
    
    return await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_PRO,
        temperature=0.8,  # Higher temperature for creative variety
        stream=False
    )


async def structure_endings_to_json(
    endings_descriptions: str,
    llm_service: LLMService
) -> List[PossibleEnding]:
    """
    Convert free-form ending descriptions to structured JSON.
    
    Args:
        endings_descriptions: Free-form descriptions of endings
        llm_service: LLMService instance
        
    Returns:
        List of PossibleEnding objects
    """
    prompt = CREATE_ENDINGS_JSON_USER_PROMPT_TEMPLATE.format(
        endings_descriptions=endings_descriptions
    )
    
    messages = [
        llm_service.create_message("system", CREATE_ENDINGS_JSON_SYSTEM_PROMPT),
        llm_service.create_message("user", prompt)
    ]
    
    response = await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_PRO,
        temperature=0.3,  # Lower temperature for more consistent output
        stream=False
    )
    
    try:
        endings_data = JSONService.parse_and_validate_json_list(response, PossibleEnding)
        return endings_data
    except Exception as e:
        raise ValueError(f"Failed to parse endings data: {str(e)}, raw response: {response}") 