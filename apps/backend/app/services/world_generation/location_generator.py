from typing import Dict, Any, List, Optional
import json
from app.services.llm import LLMService, ModelName
from app.schemas.world_generation import (
    LocationGeneratorInput,
    LocationGeneratorOutput,
    DetailedLocation,
    LocationTemplate,
    InteractiveElement
)
from app.prompts import (
    LOCATION_GENERATOR_SYSTEM_PROMPT,
    LOCATION_GENERATOR_USER_PROMPT_TEMPLATE
)


async def generate_locations(
    input_data: LocationGeneratorInput,
    llm_service: Optional[LLMService] = None
) -> LocationGeneratorOutput:
    """
    Generate detailed location profiles from basic location templates.
    
    Args:
        input_data: LocationGeneratorInput containing world setting and basic locations
        llm_service: Optional LLMService instance to use
        
    Returns:
        LocationGeneratorOutput containing detailed location profiles
    """
    # Early validation
    if not input_data.basic_locations:
        raise ValueError("No location templates provided")
    
    if not input_data.world_setting:
        raise ValueError("World setting is required")
    
    # Initialize LLM service if not provided
    llm_service = llm_service or LLMService()
    
    # Format the user prompt with input data
    user_prompt = create_location_prompt(
        input_data.world_setting.theme,
        input_data.world_setting.atmosphere,
        input_data.world_setting.description,
        input_data.basic_locations
    )
    
    # Call the LLM
    response = await call_llm(
        llm_service,
        LOCATION_GENERATOR_SYSTEM_PROMPT,
        user_prompt
    )
    
    # Parse the response and create detailed locations
    try:
        locations_data = parse_json_response(response)
        detailed_locations = create_detailed_locations(locations_data)
        return LocationGeneratorOutput(detailed_locations=detailed_locations)
    except Exception as e:
        raise ValueError(f"Failed to parse location data: {str(e)}, raw response: {response}")


def create_location_prompt(
    theme: str,
    atmosphere: Optional[str],
    description: str,
    location_templates: List[LocationTemplate]
) -> str:
    """
    Create a formatted prompt for location generation.
    
    Args:
        theme: The world theme
        atmosphere: The world atmosphere
        description: The world description
        location_templates: List of basic location templates
        
    Returns:
        Formatted prompt string
    """
    return LOCATION_GENERATOR_USER_PROMPT_TEMPLATE.format(
        theme=theme,
        atmosphere=atmosphere or "Not specified",
        setting_description=description,
        character_context="No character information available.",
        location_templates=json.dumps([loc.model_dump() for loc in location_templates], indent=2)
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
        List of location data dictionaries
    """
    if not response:
        raise ValueError("Empty response received from LLM")
        
    # Try to extract JSON from markdown code blocks if present
    json_content = extract_json_from_response(response)
    
    try:
        locations_data = json.loads(json_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    
    # Ensure we have a list of locations
    return normalize_location_data(locations_data)


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


def normalize_location_data(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize location data to ensure it's a list.
    
    Args:
        data: Location data that might be a dict or list
        
    Returns:
        List of location data dictionaries
    """
    if isinstance(data, list):
        return data
        
    if isinstance(data, dict):
        # Check if it's a dict with location keys
        if any(key.lower().startswith("location") for key in data.keys()):
            return list(data.values())
        # Single location dict
        return [data]
        
    raise ValueError(f"Unexpected data format: {type(data)}")


def create_detailed_locations(locations_data: List[Dict[str, Any]]) -> List[DetailedLocation]:
    """
    Create DetailedLocation objects from raw location data.
    
    Args:
        locations_data: List of location data dictionaries
        
    Returns:
        List of DetailedLocation objects
    """
    detailed_locations = []
    
    for loc_data in locations_data:
        # Validate required fields
        required_fields = ["id", "name", "description", "history", "atmosphere"]
        for field in required_fields:
            if field not in loc_data:
                raise ValueError(f"Missing required field '{field}' in location data")
        
        # Convert interactive elements
        interactive_elements = []
        for element in loc_data.get("interactive_elements", []):
            if isinstance(element, dict) and all(k in element for k in ["name", "description", "interaction"]):
                interactive_elements.append(
                    InteractiveElement(
                        name=element["name"],
                        description=element["description"],
                        interaction=element["interaction"]
                    )
                )
        
        if not interactive_elements:
            raise ValueError("No valid interactive elements found in location data")
            
        # Create DetailedLocation object
        detailed_location = DetailedLocation(
            id=loc_data["id"],
            name=loc_data["name"],
            description=loc_data["description"],
            history=loc_data["history"],
            atmosphere=loc_data["atmosphere"],
            interactive_elements=interactive_elements,
            connected_locations=loc_data.get("connected_locations", [])
        )
        detailed_locations.append(detailed_location)
    
    return detailed_locations 