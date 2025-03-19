from typing import Dict, Any, List, Optional
import json
from app.services.llm import LLMService, ModelName
from app.schemas.world_generation import (
    Character,
    CharactersOutput,
    World
)
from app.prompts import (
    CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE,
    DESCRIBE_CHARACTER_SYSTEM_PROMPT,
    CREATE_CHARACTER_JSON_SYSTEM_PROMPT,
    CREATE_CHARACTER_JSON_USER_PROMPT_TEMPLATE,
    CHARACTER_IMAGE_PROMPT_SYSTEM_PROMPT,
    CHARACTER_IMAGE_PROMPT_USER_TEMPLATE
)
import asyncio


async def describe_characters(
    world: World,
    llm_service: Optional[LLMService] = None
) -> str:
    """
    Generate detailed narrative descriptions of characters based on world description.
    
    Args:
        world: World object containing description and other details
        llm_service: Optional LLMService instance to use
        
    Returns:
        A detailed narrative description of the characters
    """
    
    llm_service = llm_service or LLMService()
    
    user_prompt = create_character_prompt(world.description)
    
    messages = [
        llm_service.create_message("system", DESCRIBE_CHARACTER_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]
    
    return await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_PRO,
        temperature=0.7,
        stream=False
    )


async def generate_image_prompt(
    character: Character,
    world_description: str,
    llm_service: Optional[LLMService] = None
) -> str:
    """
    Generate a detailed image prompt for a character.
    
    Args:
        character: The detailed character to generate an image prompt for
        world_description: The world description for context
        llm_service: Optional LLMService instance to use
        
    Returns:
        A detailed image prompt for the character
    """
    llm_service = llm_service or LLMService()
    
    user_prompt = CHARACTER_IMAGE_PROMPT_USER_TEMPLATE.format(
        character_name=character.name,
        character_role=character.role,
        character_appearance=character.description,
        character_description=character.backstory,
        world_description=world_description
    )
    
    messages = [
        llm_service.create_message("system", CHARACTER_IMAGE_PROMPT_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]
    
    return await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_PRO,
        temperature=0.7,
        stream=False
    )


async def generate_characters(
    world: World,
    llm_service: Optional[LLMService] = None
) -> CharactersOutput:
    """
    Generate detailed character profiles based on world description.
    
    Args:
        world: World object containing description and other details
        llm_service: Optional LLMService instance to use
        
    Returns:
        CharactersOutput containing detailed character profiles
    """
    
    llm_service = llm_service or LLMService()
    
    character_descriptions = await describe_characters(world, llm_service)
    
    user_prompt = CREATE_CHARACTER_JSON_USER_PROMPT_TEMPLATE.format(
        character_descriptions=character_descriptions
    )
    
    messages = [
        llm_service.create_message("system", CREATE_CHARACTER_JSON_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]
    
    response = await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_PRO,
        temperature=0.7,
        stream=False
    )
    
    try:
        characters_data = parse_json_response(response)
        
        characters = [Character(**char_data) for char_data in characters_data]
        
        world_description = world.description
        
        image_prompt_tasks = [
            generate_image_prompt(character, world_description, llm_service)
            for character in characters
        ]
        image_prompts = await asyncio.gather(*image_prompt_tasks)

        for character, image_prompt in zip(characters, image_prompts):
            character.imagePrompt = image_prompt
        
        return CharactersOutput(characters=characters)
    except Exception as e:
        raise ValueError(f"Failed to parse character data: {str(e)}, raw response: {response}")


def create_character_prompt(
    world_description: str
) -> str:
    """
    Create a formatted prompt for character generation.
    
    Args:
        world_description: The world description
        
    Returns:
        Formatted prompt string
    """
    return CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE.format(
        world_description=world_description
    )


async def call_llm(
    llm_service: LLMService,
    system_prompt: str,
    user_prompt: str,
    model: ModelName = ModelName.GEMINI_2_PRO,
    temperature: float = 0.7
) -> str:
    """
    Call the LLM service with the given prompts.
    
    Args:
        llm_service: The LLM service to use
        system_prompt: The system prompt
        user_prompt: The user prompt
        model: The model to use
        temperature: The temperature to use
        
    Returns:
        The LLM response
    """
    messages = [
        llm_service.create_message("system", system_prompt),
        llm_service.create_message("user", user_prompt)
    ]
    
    return await llm_service.generate_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        stream=False
    )


def parse_json_response(response: str) -> List[Dict[str, Any]]:
    """
    Parse a JSON response from the LLM.
    
    Args:
        response: The LLM response text
        
    Returns:
        List of character data dictionaries
    """
    if not response:
        raise ValueError("Empty response received from LLM")
        
    # Try to extract JSON from markdown code blocks if present
    json_content = extract_json_from_response(response)
    
    try:
        characters_data = json.loads(json_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    

    return characters_data


def extract_json_from_response(response: str) -> str:
    """
    Extract JSON content from a response that might contain markdown.
    
    Args:
        response: The response text
        
    Returns:
        Extracted JSON content as string
    """
    if "```json" in response:
        return response.split("```json")[1].split("```")[0].strip()
    elif "```" in response:
        return response.split("```")[1].split("```")[0].strip()
    else:
        return response.strip()
