from typing import Dict, Any, List, Optional
import json
from app.services.llm import LLMService, ModelName
from app.schemas.world_wizard import (
    ConflictGeneratorInput,
    ConflictGeneratorOutput,
    DetailedConflict,
    DetailedCharacter,
    DetailedLocation,
    ConflictTemplate,
    Faction,
    Resolution,
    TurningPoint,
    EntityConnection
)
from app.prompts import (
    CONFLICT_GENERATOR_SYSTEM_PROMPT,
    CONFLICT_GENERATOR_USER_PROMPT_TEMPLATE,
    DESCRIBE_CONFLICT_SYSTEM_PROMPT,
    CREATE_CONFLICT_JSON_SYSTEM_PROMPT,
    CREATE_CONFLICT_JSON_USER_PROMPT_TEMPLATE
)


async def describe_conflict(
    input_data: ConflictGeneratorInput,
    llm_service: Optional[LLMService] = None
) -> str:
    """
    Generate a detailed narrative description of a conflict.
    
    Args:
        input_data: ConflictGeneratorInput containing world setting, initial conflict, and character summaries
        llm_service: Optional LLMService instance to use
        
    Returns:
        A detailed narrative description of the conflict
    """
    # Early validation
    if not input_data.initial_conflict:
        raise ValueError("Initial conflict template is required")
    
    if not input_data.world_setting:
        raise ValueError("World setting is required")
    
    if not input_data.character_summaries:
        raise ValueError("Character summaries are required")
    
    # Initialize LLM service if not provided
    llm_service = llm_service or LLMService()
    
    # Format character and location summaries
    character_summaries = create_character_summaries(input_data.character_summaries)
    location_summaries = create_location_summaries(input_data.locations)
    
    # Format the user prompt with input data
    user_prompt = create_conflict_prompt(
        input_data.world_setting.theme,
        input_data.world_setting.atmosphere,
        input_data.world_setting.description,
        character_summaries,
        location_summaries,
        input_data.initial_conflict
    )
    
    # Call the LLM with the narrative description prompt
    messages = [
        llm_service.create_message("system", DESCRIBE_CONFLICT_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]
    
    return await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_PRO,
        temperature=0.7,
        stream=False
    )


async def generate_conflict(
    input_data: ConflictGeneratorInput,
    llm_service: Optional[LLMService] = None,
    use_two_step_process: bool = True
) -> ConflictGeneratorOutput:
    """
    Generate a detailed conflict from a basic conflict template.
    
    Args:
        input_data: ConflictGeneratorInput containing world setting, initial conflict, and character summaries
        llm_service: Optional LLMService instance to use
        use_two_step_process: Whether to use the two-step process (narrative description first, then JSON)
        
    Returns:
        ConflictGeneratorOutput containing a detailed conflict
    """
    # Early validation
    if not input_data.initial_conflict:
        raise ValueError("Initial conflict template is required")
    
    if not input_data.world_setting:
        raise ValueError("World setting is required")
    
    if not input_data.character_summaries:
        raise ValueError("Character summaries are required")
    
    # Initialize LLM service if not provided
    llm_service = llm_service or LLMService()
    
    if use_two_step_process:
        # Step 1: Generate narrative description
        conflict_description = await describe_conflict(input_data, llm_service)
        
        # Step 2: Convert narrative to structured JSON
        user_prompt = CREATE_CONFLICT_JSON_USER_PROMPT_TEMPLATE.format(
            conflict_description=conflict_description
        )
        
        messages = [
            llm_service.create_message("system", CREATE_CONFLICT_JSON_SYSTEM_PROMPT),
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
        # Format character and location summaries
        character_summaries = create_character_summaries(input_data.character_summaries)
        location_summaries = create_location_summaries(input_data.locations)
        
        # Format the user prompt with input data
        user_prompt = create_conflict_prompt(
            input_data.world_setting.theme,
            input_data.world_setting.atmosphere,
            input_data.world_setting.description,
            character_summaries,
            location_summaries,
            input_data.initial_conflict
        )
        
        # Call the LLM
        messages = [
            llm_service.create_message("system", CONFLICT_GENERATOR_SYSTEM_PROMPT),
            llm_service.create_message("user", user_prompt)
        ]
        
        response = await llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_PRO,
            temperature=0.7,
            stream=False
        )
    
    # Parse the response and create detailed conflict
    try:
        conflict_data = parse_json_response(response)
        detailed_conflict = create_detailed_conflict(conflict_data)
        return ConflictGeneratorOutput(detailed_conflict=detailed_conflict)
    except Exception as e:
        raise ValueError(f"Failed to parse conflict data: {str(e)}, raw response: {response}")


def create_character_summaries(character_summaries: List[Dict[str, str]]) -> str:
    """
    Create a formatted string of character summaries.
    
    Args:
        character_summaries: List of character summary dictionaries
        
    Returns:
        Formatted character summaries string
    """
    if not character_summaries:
        return "No character information available."
    
    summaries = []
    for char in character_summaries:
        if all(k in char for k in ["id", "name", "role"]):
            summary = f"- {char['name']} ({char['role']}): {char.get('description', 'No description available.')}"
            summaries.append(summary)
    
    return "\n".join(summaries)


def create_location_summaries(locations: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Create a formatted string of location summaries.
    
    Args:
        locations: Optional list of location summary dictionaries
        
    Returns:
        Formatted location summaries string
    """
    if not locations:
        return "No location information available."
    
    summaries = []
    for loc in locations:
        if all(k in loc for k in ["id", "name"]):
            summary = f"- {loc['name']}: {loc.get('description', 'No description available.')}"
            summaries.append(summary)
    
    return "\n".join(summaries)


def create_conflict_prompt(
    theme: str,
    atmosphere: Optional[str],
    description: str,
    character_summaries: str,
    location_summaries: str,
    initial_conflict: ConflictTemplate
) -> str:
    """
    Create a formatted prompt for conflict generation.
    
    Args:
        theme: The world theme
        atmosphere: The world atmosphere
        description: The world description
        character_summaries: Formatted character summaries
        location_summaries: Formatted location summaries
        initial_conflict: The initial conflict template
        
    Returns:
        Formatted prompt string
    """
    conflict_json = json.dumps(initial_conflict.model_dump(), indent=2)
    
    return CONFLICT_GENERATOR_USER_PROMPT_TEMPLATE.format(
        theme=theme,
        atmosphere=atmosphere or "Not specified",
        setting_description=description,
        character_summaries=character_summaries,
        location_summaries=location_summaries,
        initial_conflict=conflict_json
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


def parse_json_response(response: str) -> Dict[str, Any]:
    """
    Parse a JSON response from the LLM.
    
    Args:
        response: The LLM response text
        
    Returns:
        Parsed conflict data as a dictionary
    """
    if not response:
        raise ValueError("Empty response received from LLM")
        
    # Try to extract JSON from markdown code blocks if present
    json_content = extract_json_from_response(response)
    
    try:
        conflict_data = json.loads(json_content)
        return conflict_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")


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


def create_detailed_conflict(conflict_data: Dict[str, Any]) -> DetailedConflict:
    """
    Create a DetailedConflict object from raw conflict data.
    
    Args:
        conflict_data: Dictionary containing conflict data
        
    Returns:
        DetailedConflict object
    """
    # Validate required fields
    required_fields = ["title", "description", "factions", "stakes", "possible_resolutions"]
    for field in required_fields:
        if field not in conflict_data:
            raise ValueError(f"Missing required field '{field}' in conflict data")
    
    # Process factions
    factions = []
    for faction_data in conflict_data.get("factions", []):
        if all(k in faction_data for k in ["name", "motivation", "methods"]):
            factions.append(
                Faction(
                    name=faction_data["name"],
                    motivation=faction_data["motivation"],
                    methods=faction_data["methods"]
                )
            )
    
    if not factions:
        raise ValueError("No valid factions found in conflict data")
    
    # Process resolutions
    resolutions = []
    for resolution_data in conflict_data.get("possible_resolutions", []):
        if all(k in resolution_data for k in ["path", "description", "consequences"]):
            resolutions.append(
                Resolution(
                    path=resolution_data["path"],
                    description=resolution_data["description"],
                    consequences=resolution_data["consequences"]
                )
            )
    
    if not resolutions:
        raise ValueError("No valid resolutions found in conflict data")
    
    # Process turning points
    turning_points = []
    for tp_data in conflict_data.get("turning_points", []):
        if all(k in tp_data for k in ["trigger", "result"]):
            turning_points.append(
                TurningPoint(
                    trigger=tp_data["trigger"],
                    result=tp_data["result"]
                )
            )
    
    # Process character connections
    character_connections = []
    for cc_data in conflict_data.get("character_connections", []):
        if all(k in cc_data for k in ["character_id", "involvement"]):
            character_connections.append(
                EntityConnection(
                    entity_id=cc_data["character_id"],
                    connection=cc_data["involvement"]
                )
            )
    
    # Process location connections
    location_connections = []
    for lc_data in conflict_data.get("location_connections", []):
        if all(k in lc_data for k in ["location_id", "significance"]):
            location_connections.append(
                EntityConnection(
                    entity_id=lc_data["location_id"],
                    connection=lc_data["significance"]
                )
            )
    
    # Process stakes
    stakes = conflict_data.get("stakes", {})
    personal_stakes = stakes.get("personal", "Unknown personal stakes")
    community_stakes = stakes.get("community", "Unknown community stakes")
    world_stakes = stakes.get("world", "Unknown world stakes")
    
    # Create the DetailedConflict object
    return DetailedConflict(
        title=conflict_data["title"],
        description=conflict_data["description"],
        factions=factions,
        possible_resolutions=resolutions,
        turning_points=turning_points or [],
        character_connections=character_connections or [],
        location_connections=location_connections or [],
        personal_stakes=personal_stakes,
        community_stakes=community_stakes,
        world_stakes=world_stakes
    ) 