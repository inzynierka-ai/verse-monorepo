from typing import Dict, Any, List, Optional
import json
from app.services.llm import LLMService, ModelName
from app.schemas.world_wizard import (
    WorldCoordinatorInput,
    WorldCoordinatorOutput,
    FinalGameWorld,
    CharacterConnection,
    LocationConnection,
    StoryHook,
    WorldRule,
    DetailedCharacter,
    DetailedLocation,
    DetailedConflict,
    SettingInfo
)
from app.prompts import (
    WORLD_COORDINATOR_SYSTEM_PROMPT,
    WORLD_COORDINATOR_USER_PROMPT_TEMPLATE
)


async def coordinate_world(
    input_data: WorldCoordinatorInput,
    llm_service: Optional[LLMService] = None
) -> WorldCoordinatorOutput:
    """
    Coordinate a complete game world by integrating detailed characters, locations, and conflict.
    
    Args:
        input_data: WorldCoordinatorInput containing all the detailed game elements
        llm_service: Optional LLMService instance to use
        
    Returns:
        WorldCoordinatorOutput containing the final game world
    """
    # Early validation
    if not input_data.world_setting:
        raise ValueError("World setting is required")
    
    if not input_data.detailed_characters or len(input_data.detailed_characters) == 0:
        raise ValueError("At least one detailed character is required")
    
    if not input_data.detailed_locations or len(input_data.detailed_locations) == 0:
        raise ValueError("At least one detailed location is required")
    
    if not input_data.detailed_conflict:
        raise ValueError("Detailed conflict is required")
    
    # Initialize LLM service if not provided
    llm_service = llm_service or LLMService()
    
    # Prepare the input data for the LLM
    setting_json = json.dumps(input_data.world_setting.model_dump(), indent=2)
    characters_json = json.dumps([c.model_dump() for c in input_data.detailed_characters], indent=2)
    locations_json = json.dumps([l.model_dump() for l in input_data.detailed_locations], indent=2)
    conflict_json = json.dumps(input_data.detailed_conflict.model_dump(), indent=2)
    
    # Format the user prompt with input data
    user_prompt = create_coordination_prompt(
        setting_json,
        characters_json,
        locations_json,
        conflict_json
    )
    
    # Call the LLM
    response = await call_llm(
        llm_service,
        WORLD_COORDINATOR_SYSTEM_PROMPT,
        user_prompt
    )
    
    # Parse the response and create the final game world
    try:
        world_data = parse_json_response(response)
        final_game_world = create_final_game_world(world_data)
        return WorldCoordinatorOutput(final_game_world=final_game_world)
    except Exception as e:
        raise ValueError(f"Failed to parse world coordination data: {str(e)}, raw response: {response}")


def create_coordination_prompt(
    setting_json: str,
    characters_json: str,
    locations_json: str,
    conflict_json: str
) -> str:
    """
    Create a formatted prompt for world coordination.
    
    Args:
        setting_json: JSON string of world setting
        characters_json: JSON string of detailed characters
        locations_json: JSON string of detailed locations
        conflict_json: JSON string of detailed conflict
        
    Returns:
        Formatted prompt string
    """
    return WORLD_COORDINATOR_USER_PROMPT_TEMPLATE.format(
        setting_json=setting_json,
        characters_json=characters_json,
        locations_json=locations_json,
        conflict_json=conflict_json
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
        Parsed world data as a dictionary
    """
    if not response:
        raise ValueError("Empty response received from LLM")
        
    # Try to extract JSON from markdown code blocks if present
    json_content = extract_json_from_response(response)
    
    try:
        world_data = json.loads(json_content)
        return world_data
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


def create_final_game_world(world_data: Dict[str, Any]) -> FinalGameWorld:
    """
    Create a FinalGameWorld object from raw world data.
    
    Args:
        world_data: Dictionary containing final game world data
        
    Returns:
        FinalGameWorld object
    """
    # Validate required fields
    required_fields = ["setting_summary", "character_connections", "location_connections", 
                       "story_hooks", "world_rules", "cohesion_notes"]
    for field in required_fields:
        if field not in world_data:
            raise ValueError(f"Missing required field '{field}' in world data")
    
    # Process character connections
    character_connections = []
    for cc_data in world_data.get("character_connections", []):
        if all(k in cc_data for k in ["character_id", "connected_locations", "involvement_in_conflict"]):
            character_connections.append(
                CharacterConnection(
                    character_id=cc_data["character_id"],
                    connected_locations=cc_data["connected_locations"],
                    involvement_in_conflict=cc_data["involvement_in_conflict"]
                )
            )
    
    if not character_connections:
        raise ValueError("No valid character connections found in world data")
    
    # Process location connections
    location_connections = []
    for lc_data in world_data.get("location_connections", []):
        if all(k in lc_data for k in ["location_id", "connected_characters", "role_in_conflict"]):
            location_connections.append(
                LocationConnection(
                    location_id=lc_data["location_id"],
                    connected_characters=lc_data["connected_characters"],
                    role_in_conflict=lc_data["role_in_conflict"]
                )
            )
    
    if not location_connections:
        raise ValueError("No valid location connections found in world data")
    
    # Process story hooks
    story_hooks = []
    for sh_data in world_data.get("story_hooks", []):
        if all(k in sh_data for k in ["title", "description", "involving_characters", "involving_locations"]):
            story_hooks.append(
                StoryHook(
                    title=sh_data["title"],
                    description=sh_data["description"],
                    involving_characters=sh_data["involving_characters"],
                    involving_locations=sh_data["involving_locations"]
                )
            )
    
    if not story_hooks:
        raise ValueError("No valid story hooks found in world data")
    
    # Process world rules
    world_rules = []
    for wr_data in world_data.get("world_rules", []):
        if all(k in wr_data for k in ["name", "description"]):
            world_rules.append(
                WorldRule(
                    name=wr_data["name"],
                    description=wr_data["description"]
                )
            )
    
    if not world_rules:
        raise ValueError("No valid world rules found in world data")
    
    # Create the FinalGameWorld object
    return FinalGameWorld(
        setting_summary=world_data["setting_summary"],
        character_connections=character_connections,
        location_connections=location_connections,
        story_hooks=story_hooks,
        world_rules=world_rules,
        cohesion_notes=world_data["cohesion_notes"]
    ) 