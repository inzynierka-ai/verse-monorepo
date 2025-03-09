from typing import Dict, Any, List, Optional
import json
from app.services.llm import LLMService, ModelName
from app.schemas.world_wizard import (
    CharacterGeneratorInput,
    CharacterGeneratorOutput,
    DetailedCharacter,
    PersonalityTrait,
    CharacterTemplate
)
from app.prompts import (
    CHARACTER_GENERATOR_SYSTEM_PROMPT,
    CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE,
    DESCRIBE_CHARACTER_SYSTEM_PROMPT,
    CREATE_CHARACTER_JSON_SYSTEM_PROMPT,
    CREATE_CHARACTER_JSON_USER_PROMPT_TEMPLATE
)


async def describe_characters(
    input_data: CharacterGeneratorInput,
    llm_service: Optional[LLMService] = None
) -> str:
    """
    Generate detailed narrative descriptions of characters from basic character templates.
    
    Args:
        input_data: CharacterGeneratorInput containing world setting and basic characters
        llm_service: Optional LLMService instance to use
        
    Returns:
        A detailed narrative description of the characters
    """
    # Early validation
    if not input_data.basic_characters:
        raise ValueError("No character templates provided")
    
    if not input_data.world_setting:
        raise ValueError("World setting is required")
    
    # Initialize LLM service if not provided
    llm_service = llm_service or LLMService()
    
    # Format the user prompt with input data
    user_prompt = create_character_prompt(
        input_data.world_setting.theme,
        input_data.world_setting.atmosphere,
        input_data.world_setting.description,
        input_data.basic_characters
    )
    
    # Call the LLM with the narrative description prompt
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


async def generate_characters(
    input_data: CharacterGeneratorInput,
    llm_service: Optional[LLMService] = None,
    use_two_step_process: bool = True
) -> CharacterGeneratorOutput:
    """
    Generate detailed character profiles from basic character templates.
    
    Args:
        input_data: CharacterGeneratorInput containing world setting and basic characters
        llm_service: Optional LLMService instance to use
        use_two_step_process: Whether to use the two-step process (narrative description first, then JSON)
        
    Returns:
        CharacterGeneratorOutput containing detailed character profiles
    """
    # Early validation
    if not input_data.basic_characters:
        raise ValueError("No character templates provided")
    
    if not input_data.world_setting:
        raise ValueError("World setting is required")
    
    # Initialize LLM service if not provided
    llm_service = llm_service or LLMService()
    
    if use_two_step_process:
        # Step 1: Generate narrative descriptions
        character_descriptions = await describe_characters(input_data, llm_service)
        
        # Step 2: Convert narrative to structured JSON
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
    else:
        # Original single-step process
        # Format the user prompt with input data
        user_prompt = create_character_prompt(
            input_data.world_setting.theme,
            input_data.world_setting.atmosphere,
            input_data.world_setting.description,
            input_data.basic_characters
        )
        
        # Call the LLM
        messages = [
            llm_service.create_message("system", CHARACTER_GENERATOR_SYSTEM_PROMPT),
            llm_service.create_message("user", user_prompt)
        ]
        
        response = await llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_PRO,
            temperature=0.7,
            stream=False
        )
    
    # Parse the response and create detailed characters
    try:
        characters_data = parse_json_response(response)
        detailed_characters = create_detailed_characters(characters_data)
        return CharacterGeneratorOutput(detailed_characters=detailed_characters)
    except Exception as e:
        raise ValueError(f"Failed to parse character data: {str(e)}, raw response: {response}")


def create_character_prompt(
    theme: str,
    atmosphere: Optional[str],
    description: str,
    character_templates: List[CharacterTemplate]
) -> str:
    """
    Create a formatted prompt for character generation.
    
    Args:
        theme: The world theme
        atmosphere: The world atmosphere
        description: The world description
        character_templates: List of basic character templates
        
    Returns:
        Formatted prompt string
    """
    return CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE.format(
        theme=theme,
        atmosphere=atmosphere or "Not specified",
        setting_description=description,
        character_templates=json.dumps([char.model_dump() for char in character_templates], indent=2)
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
    
    # Ensure we have a list of characters
    return normalize_character_data(characters_data)


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


def normalize_character_data(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize character data to ensure it's a list.
    
    Args:
        data: Character data that might be a dict or list
        
    Returns:
        List of character data dictionaries
    """
    if isinstance(data, list):
        return data
        
    if isinstance(data, dict):
        # Check if it's a dict with character keys
        if any(key.lower().startswith("character") for key in data.keys()):
            return list(data.values())
        # Single character dict
        return [data]
        
    raise ValueError(f"Unexpected data format: {type(data)}")


def create_detailed_characters(characters_data: List[Dict[str, Any]]) -> List[DetailedCharacter]:
    """
    Create DetailedCharacter objects from raw character data.
    
    Args:
        characters_data: List of character data dictionaries
        
    Returns:
        List of DetailedCharacter objects
    """
    detailed_characters = []
    
    for char_data in characters_data:
        # Validate required fields
        required_fields = ["id", "name", "role", "description", "backstory", "goals", "appearance"]
        for field in required_fields:
            if field not in char_data:
                raise ValueError(f"Missing required field '{field}' in character data")
        
        # Convert personality traits
        personality_traits = [
            PersonalityTrait(name=trait["name"], description=trait["description"])
            for trait in char_data.get("personality_traits", [])
        ]
        
        # Create DetailedCharacter object
        detailed_character = DetailedCharacter(
            id=char_data["id"],
            name=char_data["name"],
            role=char_data["role"],
            description=char_data["description"],
            personality_traits=personality_traits,
            backstory=char_data["backstory"],
            goals=char_data["goals"],
            appearance=char_data["appearance"],
            relationships=[]  # Relationships will be added later if needed
        )
        detailed_characters.append(detailed_character)
    
    return detailed_characters 