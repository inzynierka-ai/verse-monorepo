import asyncio
import json
import re
from typing import Dict, Any, List, Optional

from app.services.llm import LLMService, ModelName
from app.services.world_generation.world_wizard import WorldWizard
from app.services.world_generation.character_generator import generate_characters
from app.services.world_generation.location_generator import generate_locations
from app.services.world_generation.conflict_generator import generate_conflict
from app.services.world_generation.narrator import Narrator

from app.schemas.world_wizard import (
    WorldSettings,
    CharacterGeneratorInput,
    LocationGeneratorInput,
    ConflictGeneratorInput,
    FinalGameWorld,
    WorldTemplate,
    CharacterConnection,
    LocationConnection,
    StoryHook,
    WorldRule
)

from app.prompts import (
    WORLD_COORDINATOR_SYSTEM_PROMPT,
    WORLD_COORDINATOR_USER_PROMPT_TEMPLATE
)


class WorldGenerationError(Exception):
    """Exception raised for errors in the world generation process."""
    pass


class QuotaExceededError(WorldGenerationError):
    """Exception raised when API quota limits are exceeded."""
    pass


async def generate_complete_world(
    settings: WorldSettings,
    llm_service: Optional[LLMService] = None
) -> Dict[str, Any]:
    """
    Generate a complete world from simple input settings, orchestrating the entire pipeline.
    
    Args:
        settings: WorldSettings containing theme and optional parameters
        llm_service: Optional LLMService instance to use
        
    Returns:
        Dictionary containing the complete generated world
    """
    # Initialize LLM service if not provided
    llm_service = llm_service or LLMService()
    
    try:
        # Step 1: Generate world template using the World Wizard
        print("Step 1/5: Generating world template...")
        world_template = await generate_world_template(settings, llm_service)
        print("✓ World template generated")
        
        # Step 2: Generate detailed characters and locations in parallel
        character_input = CharacterGeneratorInput(
            world_setting=world_template.setting,
            basic_characters=world_template.basic_characters
        )
        
        location_input = LocationGeneratorInput(
            world_setting=world_template.setting,
            basic_locations=world_template.basic_locations
        )
        
        # Run character and location generation concurrently
        print("Step 2/5: Generating characters and locations...")
        character_task = generate_characters(character_input, llm_service)
        location_task = generate_locations(location_input, llm_service)
        
        # Await both tasks to complete
        character_output, location_output = await asyncio.gather(character_task, location_task)
        
        detailed_characters = character_output.detailed_characters
        detailed_locations = location_output.detailed_locations
        print(f"✓ Generated {len(detailed_characters)} characters and {len(detailed_locations)} locations")
        
        # Step 3: Generate detailed conflict
        print("Step 3/5: Generating conflict...")
        character_summaries = []
        for char in detailed_characters:
            character_summaries.append({
                "id": char.id,
                "name": char.name,
                "role": char.role,
                "description": char.description
            })
        
        location_summaries = []
        for loc in detailed_locations:
            location_summaries.append({
                "id": loc.id,
                "name": loc.name,
                "description": loc.description
            })
        
        conflict_input = ConflictGeneratorInput(
            world_setting=world_template.setting,
            initial_conflict=world_template.initial_conflict,
            character_summaries=character_summaries,
            locations=location_summaries
        )
        
        conflict_output = await generate_conflict(conflict_input, llm_service)
        detailed_conflict = conflict_output.detailed_conflict
        print(f"✓ Conflict '{detailed_conflict.title}' generated")
        
        # Step 4: Integrate all components directly instead of using world_coordinator
        print("Step 4/5: Integrating world components...")
        final_world = await integrate_world_components(
            world_setting=world_template.setting,
            detailed_characters=detailed_characters,
            detailed_locations=detailed_locations,
            detailed_conflict=detailed_conflict,
            llm_service=llm_service
        )
        print(f"✓ World components integrated with {len(final_world.story_hooks)} story hooks")
        
        # Step 5: Prepare the final output
        print("Step 5/5: Formatting final output...")
        result = format_final_output(
            final_world,
            detailed_characters,
            detailed_locations,
            detailed_conflict
        )
        print("✓ World generation complete")
        
        return result
        
    except QuotaExceededError as qe:
        print(f"❌ API quota exceeded: {str(qe)}")
        # Return immediately to halt the process
        raise
    except Exception as e:
        print(f"❌ Error during world generation: {str(e)}")
        raise WorldGenerationError(f"Error during world generation: {str(e)}")


async def generate_world_template(
    settings: WorldSettings,
    llm_service: LLMService
) -> WorldTemplate:
    """
    Generate a world template using the World Wizard.
    
    Args:
        settings: WorldSettings containing theme and optional parameters
        llm_service: LLMService instance to use
        
    Returns:
        Generated WorldTemplate
    """
    try:
        world_wizard = WorldWizard(llm_service)
        return await world_wizard.create_world_template(settings)
    except Exception as e:
        # Check if this is a quota exceeded error
        if is_quota_exceeded_error(str(e)):
            raise QuotaExceededError(f"API quota exceeded while generating world template: {str(e)}")
        raise WorldGenerationError(f"Error generating world template: {str(e)}")


async def integrate_world_components(
    world_setting,
    detailed_characters,
    detailed_locations,
    detailed_conflict,
    llm_service: LLMService
) -> FinalGameWorld:
    """
    Integrate all generated components into a cohesive final game world.
    This directly performs what world_coordinator used to do.
    
    Args:
        world_setting: The world setting
        detailed_characters: List of detailed character profiles
        detailed_locations: List of detailed location profiles
        detailed_conflict: The detailed conflict scenario
        llm_service: LLM service instance
        
    Returns:
        A FinalGameWorld object with all components integrated
    """
    # Prepare the input data for the LLM
    setting_json = json.dumps(world_setting.model_dump(), indent=2)
    characters_json = json.dumps([c.model_dump() for c in detailed_characters], indent=2)
    locations_json = json.dumps([l.model_dump() for l in detailed_locations], indent=2)
    conflict_json = json.dumps(detailed_conflict.model_dump(), indent=2)
    
    # Format the user prompt
    user_prompt = WORLD_COORDINATOR_USER_PROMPT_TEMPLATE.format(
        setting_json=setting_json,
        characters_json=characters_json,
        locations_json=locations_json,
        conflict_json=conflict_json
    )
    
    # Call the LLM
    messages = [
        llm_service.create_message("system", WORLD_COORDINATOR_SYSTEM_PROMPT),
        llm_service.create_message("user", user_prompt)
    ]
    
    try:
        response = await llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_PRO,
            temperature=0.7,
            stream=False
        )
        
        # Parse the response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                json_content = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_content = response.split("```")[1].split("```")[0].strip()
            else:
                json_content = response.strip()
            
            world_data = json.loads(json_content)
            
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
            
            # Create the FinalGameWorld object
            return FinalGameWorld(
                setting_summary=world_data["setting_summary"],
                character_connections=character_connections,
                location_connections=location_connections,
                story_hooks=story_hooks,
                world_rules=world_rules,
                cohesion_notes=world_data["cohesion_notes"]
            )
        
        except Exception as e:
            raise WorldGenerationError(f"Failed to integrate world components: {str(e)}")
    
    except Exception as e:
        # Check if this is a quota exceeded error
        if is_quota_exceeded_error(str(e)):
            raise QuotaExceededError(f"API quota exceeded while integrating world components: {str(e)}")
        raise WorldGenerationError(f"Error during world component integration: {str(e)}")


def is_quota_exceeded_error(error_message: str) -> bool:
    """
    Check if an error message indicates a quota exceeded error.
    
    Args:
        error_message: The error message to check
        
    Returns:
        True if the error message indicates a quota exceeded error, False otherwise
    """
    # Check for the specific Google API quota exceeded error message
    quota_patterns = [
        "Quota exceeded",
        "RESOURCE_EXHAUSTED",
        "429",
        "generate_content_requests_per_minute_per_project_per_base_model"
    ]
    
    for pattern in quota_patterns:
        if pattern in error_message:
            return True
    
    return False


def format_final_output(
    final_world: FinalGameWorld,
    detailed_characters: List,
    detailed_locations: List,
    detailed_conflict: Any
) -> Dict[str, Any]:
    """
    Format the final output for the complete world.
    
    Args:
        final_world: The coordinated final game world
        detailed_characters: List of detailed characters
        detailed_locations: List of detailed locations
        detailed_conflict: Detailed conflict
        
    Returns:
        Formatted dictionary with the complete world
    """
    # Format the output as expected by the JSON schema
    formatted_output = {
        "setting": {
            "summary": final_world.setting_summary
        },
        "characters": [char.model_dump() for char in detailed_characters],
        "locations": [loc.model_dump() for loc in detailed_locations],
        "conflict": detailed_conflict.model_dump(),
        "connections": {
            "character_connections": [cc.model_dump() for cc in final_world.character_connections],
            "location_connections": [lc.model_dump() for lc in final_world.location_connections]
        },
        "story_hooks": [hook.model_dump() for hook in final_world.story_hooks],
        "world_rules": [rule.model_dump() for rule in final_world.world_rules],
        "cohesion_notes": final_world.cohesion_notes
    }
    
    # The introduction will be generated separately by the frontend
    # rather than here to avoid blocking the response
    formatted_output["introduction"] = []
    
    return formatted_output


async def generate_introduction_for_world(world_data: Dict[str, Any], llm_service: Optional[LLMService] = None) -> List[Dict[str, str]]:
    """
    Generate an immersive introduction for a world after it has been created.
    This is a separate function that can be called by the frontend when needed.
    
    Args:
        world_data: The complete world data
        llm_service: Optional LLMService instance
        
    Returns:
        A list of introduction steps with titles and content
    """
    try:
        llm_service = llm_service or LLMService()
        narrator = Narrator(world_data, llm_service)
        return await narrator.generate_introduction(use_llm=True)
    except Exception as e:
        print(f"Error generating introduction: {str(e)}")
        # Return a minimal introduction with error info
        return [{
            "title": "Introduction",
            "content": "The world awaits your exploration. (Error generating detailed introduction.)"
        }] 