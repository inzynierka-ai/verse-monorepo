import json
import re
import logging
from typing import Dict, Any, List, Optional

from app.services.llm import LLMService, ModelName
from app.prompts.narrator_prompts import (
    NARRATOR_SYSTEM_PROMPT,
    SETTING_PROMPT_TEMPLATE,
    CHARACTER_PROMPT_TEMPLATE,
    CONFLICT_PROMPT_TEMPLATE,
    LOCATION_PROMPT_TEMPLATE,
    CALL_TO_ACTION_PROMPT_TEMPLATE
)
from app.schemas.world_generation import IntroductionOutput, Character, Location, World, ChapterOutput

logger = logging.getLogger(__name__)


async def generate_introduction(
    world_data: Dict[str, Any],  # Keep as Dict for now since we need additional chapter data
    player_character: Character,
    starting_location: Location, 
    use_llm: bool = True, 
    llm_service: Optional[LLMService] = None
) -> IntroductionOutput:
    """
    Generate a 5-step immersive introduction based on the world data.
    
    Args:
        world_data: World generation output as a dictionary
        player_character: The player character model
        starting_location: The starting location model
        use_llm: Whether to use LLM enhancement (defaults to True)
        llm_service: Optional LLMService instance
        
    Returns:
        IntroductionOutput containing the introduction steps
    """
    llm_service = llm_service or LLMService()
    
    if use_llm:
        try:
            # Use LLM for enhanced narration
            steps = await generate_llm_introduction(world_data, player_character, starting_location, llm_service)
            return IntroductionOutput(steps=steps)
        except Exception as e:
            logger.warning(f"LLM introduction generation failed: {str(e)}")
            logger.warning("Falling back to template-based introduction...")
    
    # Fallback to template-based introduction
    steps = generate_template_introduction(world_data, player_character, starting_location)
    return IntroductionOutput(steps=steps)


async def generate_llm_introduction(
    world_data: Dict[str, Any],
    player_character: Character,
    starting_location: Location,
    llm_service: LLMService
) -> List[str]:
    """
    Generate an immersive introduction using LLM.
    
    Args:
        world_data: World generation output as a dictionary
        player_character: The player character model
        starting_location: The starting location model
        llm_service: LLMService instance
        
    Returns:
        A list of strings with introduction step content
    """
    # Prepare prompts for each step
    prompt_tuples = [
        prepare_setting_prompt(world_data),
        prepare_character_prompt(player_character),
        prepare_conflict_prompt(world_data),
        prepare_location_prompt(starting_location),
        prepare_call_to_action_prompt(player_character, world_data)
    ]
    
    # Generate content for each step
    results = []
    for prompt in prompt_tuples:
        content = await generate_llm_content(prompt, llm_service)
        results.append(content)
            
    return results


async def generate_llm_content(prompt: str, llm_service: LLMService) -> str:
    """
    Generate content using LLM.
    
    Args:
        prompt: The prompt to send to the LLM
        llm_service: LLMService instance
        
    Returns:
        The generated content
    """
    messages = [
        llm_service.create_message("system", NARRATOR_SYSTEM_PROMPT),
        llm_service.create_message("user", prompt)
    ]
    
    response = await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_PRO,
        temperature=0.8,
        stream=False
    )
    
    # Clean up the response
    result = format_text(response)
    
    return result


def generate_template_introduction(
    world_data: Dict[str, Any],
    player_character: Character,
    starting_location: Location
) -> List[str]:
    """
    Generate a template-based introduction without using LLM.
    
    Args:
        world_data: World generation output as a dictionary
        player_character: The player character model
        starting_location: The starting location model
        
    Returns:
        A list of strings with introduction step content
    """
    # Generate content for each step using templates
    steps = [
        generate_setting_establishment(world_data),
        generate_character_introduction(player_character),
        generate_conflict_glimpse(world_data),
        generate_location_focus(starting_location),
        generate_call_to_action(player_character, world_data)
    ]
    
    return steps


def format_text(text: str) -> str:
    """
    Format text for better readability and presentation.
    
    Args:
        text: The text to format
        
    Returns:
        Formatted text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Ensure the text ends with a period
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
        
    return text


def extract_first_sentences(text: str, count: int = 2) -> str:
    """
    Extract the first N sentences from a text.
    
    Args:
        text: The text to extract from
        count: Number of sentences to extract
        
    Returns:
        The extracted sentences
    """
    if not text:
        return ""
        
    # Split by sentence endings followed by a space
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Take the requested number of sentences
    selected = sentences[:count]
    
    # Join and return
    result = " ".join(selected)
    
    # Ensure it ends with proper punctuation
    if result and not result.endswith(('.', '!', '?')):
        result += '.'
        
    return result


# Prompt preparation functions
def prepare_setting_prompt(world_data: Dict[str, Any]) -> str:
    """Prepare prompt for setting establishment."""
    # Extract World data from chapter data
    world = world_data.get("world", {})
    setting_summary = world.get("description", "")
    
    # Get relevant world rules
    world_rules = world.get("rules", [])
    rules_text = ""
    for i, rule in enumerate(world_rules[:3]):  # Include up to 3 rules
        rules_text += f"- {rule}\n"
    
    return SETTING_PROMPT_TEMPLATE.format(
        setting_summary=setting_summary,
        rules_text=rules_text
    )


def prepare_character_prompt(player_character: Character) -> str:
    """Prepare prompt for character introduction."""
    name = player_character.name
    description = player_character.description
    backstory = player_character.backstory
    
    # Get personality traits
    traits = player_character.personalityTraits or []
    traits_text = "\n".join([f"- {trait}" for trait in traits[:3]])
    
    # Goals
    goals = player_character.goals
    goals_text = "\n".join([f"- {goal}" for goal in goals[:3]])
    
    return CHARACTER_PROMPT_TEMPLATE.format(
        name=name,
        description=description,
        backstory=backstory,
        traits_text=traits_text,
        goals_text=goals_text
    )


def prepare_conflict_prompt(world_data: Dict[str, Any]) -> str:
    """Prepare prompt for conflict glimpse."""
    conflict = world_data.get("conflict", {})
    title = conflict.get("title", "")
    description = conflict.get("description", "")
    
    # Get faction information
    factions = conflict.get("factions", [])
    factions_text = ""
    for faction in factions[:2]:  # Include up to 2 factions
        factions_text += f"- {faction.get('name', '')}: {faction.get('motivation', '')}\n"
    
    # Stakes
    personal_stakes = conflict.get("personal_stakes", "")
    world_stakes = conflict.get("world_stakes", "")
    
    return CONFLICT_PROMPT_TEMPLATE.format(
        title=title,
        description=description,
        factions_text=factions_text,
        personal_stakes=personal_stakes,
        world_stakes=world_stakes
    )


def prepare_location_prompt(location: Location) -> str:
    """Prepare prompt for location focus."""
    name = location.name
    description = location.description
    
    # Get atmosphere from rules if available
    atmosphere = ""
    for rule in location.rules:
        if "atmosphere" in rule.lower():
            atmosphere = rule
            break
    
    # Get interactive elements (simplified for demonstration)
    elements_text = ""
    for i, rule in enumerate(location.rules[:2]):
        if not "atmosphere" in rule.lower():
            elements_text += f"- {rule}\n"
    
    return LOCATION_PROMPT_TEMPLATE.format(
        name=name,
        description=description,
        atmosphere=atmosphere,
        elements_text=elements_text
    )


def prepare_call_to_action_prompt(player_character: Character, world_data: Dict[str, Any]) -> str:
    """Prepare prompt for call to action."""
    # Get player goals
    goals = player_character.goals
    first_goal = goals[0] if goals else "Uncover the truth"
    
    # Get story hooks
    story_hooks = world_data.get("story_hooks", [])
    hooks_text = ""
    for hook in story_hooks[:2]:  # Include up to 2 hooks
        hooks_text += f"- {hook.get('title', '')}: {hook.get('description', '')}\n"
    
    # Get conflict info
    conflict = world_data.get("conflict", {})
    possible_resolutions = conflict.get("possible_resolutions", [])
    resolutions_text = ""
    for resolution in possible_resolutions[:2]:  # Include up to 2 resolutions
        resolutions_text += f"- {resolution.get('path', '')}: {resolution.get('description', '')}\n"
    
    return CALL_TO_ACTION_PROMPT_TEMPLATE.format(
        first_goal=first_goal,
        hooks_text=hooks_text,
        resolutions_text=resolutions_text
    )


# Template-based generation functions
def generate_setting_establishment(world_data: Dict[str, Any]) -> str:
    """Generate the first step: Setting Establishment using templates."""
    # Extract World data from chapter data
    world = world_data.get("world", {})
    setting_summary = world.get("description", "")
    world_rules = world.get("rules", [])
    
    # Create content with 3-4 sentences
    content = format_text(setting_summary)
    
    # If the setting is too long, extract just the first 2-3 sentences
    if len(content.split()) > 80:
        content = extract_first_sentences(content, 3)
    
    if world_rules and len(world_rules) > 0:
        rule = world_rules[0]
        rule_desc = extract_first_sentences(rule, 1)
        content += f" {rule_desc}"
        
    # Add a final sentence about the world's current state
    content += " The world stands at a crossroads, with forces in motion that will shape its destiny."
        
    return content


def generate_character_introduction(player_character: Character) -> str:
    """Generate the second step: Character Introduction using templates."""
    name = player_character.name
    description = player_character.description
    backstory = player_character.backstory
    
    # Get personality traits
    trait_descriptions = player_character.personalityTraits or []
    
    # Create content with 3-4 sentences
    content = f"You are {name}."
    
    # Add first 1-2 sentences of description
    if description:
        desc_intro = extract_first_sentences(description, 2)
        content += f" {desc_intro}"
    
    # Add one personality trait
    if trait_descriptions:
        trait = format_text(trait_descriptions[0])
        content += f" {trait}"
        
    # Add first sentence of backstory
    if backstory:
        backstory_intro = extract_first_sentences(backstory, 1)
        content += f" {backstory_intro}"
    
    return content


def generate_conflict_glimpse(world_data: Dict[str, Any]) -> str:
    """Generate the third step: Conflict Glimpse using templates."""
    conflict = world_data.get("conflict", {})
    title = conflict.get("title", "")
    description = conflict.get("description", "")
    
    # Try to find the first sentence or a short excerpt
    first_sentence = ""
    if description:
        first_sentence = extract_first_sentences(description, 1)
    else:
        first_sentence = "A conflict brews in the shadows, its true nature yet to be revealed."
    
    # Get faction info
    factions = conflict.get("factions", [])
    faction_info = ""
    if factions and len(factions) > 0:
        faction = factions[0]
        name = faction.get('name', 'unknown forces')
        methods = extract_first_sentences(faction.get('methods', ''), 1)
        if methods:
            faction_info = f"The {name} {methods}"
    
    # Add stakes
    personal_stakes = conflict.get("personal_stakes", "")
    
    # Create content with 3-4 sentences
    content = first_sentence
    
    if faction_info:
        content += f" {faction_info}"
        
    if personal_stakes:
        stakes = extract_first_sentences(personal_stakes, 1)
        content += f" {stakes}"
    else:
        content += " The consequences of failure are dire, both for you and for everyone around you."
        
    # Add a final sentence about the conflict's immediacy
    content += " Time is not on your side, and decisions must be made soon."
    
    # Final formatting
    content = format_text(content)
    
    return content


def generate_location_focus(location: Location) -> str:
    """Generate the fourth step: Location Focus using templates."""
    name = location.name
    description = location.description
    
    # Extract atmosphere from rules if available
    atmosphere = ""
    for rule in location.rules:
        if "atmosphere" in rule.lower():
            atmosphere = rule
            break
    
    # Create content with 3-4 sentences
    content = f"You find yourself in {name}."
    
    if description:
        # Extract only 1-2 sentences of the description to keep it concise
        desc_excerpt = extract_first_sentences(description, 2)
        content += f" {desc_excerpt}"
            
    if atmosphere:
        # Extract first sentence of atmosphere
        atmos_sentence = extract_first_sentences(atmosphere, 1)
        content += f" {atmos_sentence}"
        
    # Final formatting
    content = format_text(content)
        
    return content


def generate_call_to_action(player_character: Character, world_data: Dict[str, Any]) -> str:
    """Generate the fifth step: Call to Action using templates."""
    # Get player goals
    goals = player_character.goals
    first_goal = goals[0] if goals else "Uncover the truth"
    
    # Get story hooks for potential directions
    story_hooks = world_data.get("story_hooks", [])
    hook_direction = ""
    if story_hooks and len(story_hooks) > 0:
        hook = story_hooks[0]
        hook_description = hook.get('description', '')
        if hook_description:
            hook_direction = extract_first_sentences(hook_description, 1)
    
    # Get world stakes
    world_stakes = world_data.get("conflict", {}).get("world_stakes", "")
    
    # Create content with 3-4 sentences
    content = f"Your journey begins with a clear purpose: {first_goal}."
    
    if hook_direction:
        content += f" {hook_direction}"
        
    if world_stakes:
        stakes = extract_first_sentences(world_stakes, 1)
        content += f" {stakes}"
    else:
        content += " The fate of this world may well rest on your shoulders."
        
    # Final call to action
    content += " The path forward is uncertain, but you must take the first step."
    
    # Final formatting
    content = format_text(content)
    
    return content


async def from_json_file(file_path: str, llm_service: Optional[LLMService] = None) -> IntroductionOutput:
    """
    Generate an introduction from a JSON file.
    
    Args:
        file_path: Path to the JSON file with world data
        llm_service: Optional LLMService instance
        
    Returns:
        IntroductionOutput instance
    """
    with open(file_path, 'r') as f:
        world_data = json.load(f)
        
    from app.schemas.world_generation import Character, Location, ChapterOutput
    from pydantic import parse_obj_as
    
    # Try to parse as ChapterOutput if possible
    try:
        chapter_data = parse_obj_as(ChapterOutput, world_data)
        
        # Extract world, a character and a location from the chapter data
        world_data = world_data  # Use raw dict as it may contain conflict data not in the World model
        player_character = next((c for c in chapter_data.characters if c.role.lower() == "player"), chapter_data.characters[0] if chapter_data.characters else None)
        starting_location = chapter_data.locations[0] if chapter_data.locations else None
        
        if not player_character or not starting_location:
            raise ValueError("Could not find player character or starting location in world data")
        
        return await generate_introduction(world_data, player_character, starting_location, True, llm_service)
    except Exception as e:
        logger.warning(f"Failed to parse as ChapterOutput: {str(e)}")
        
        # Fall back to manual extraction
        characters = parse_obj_as(List[Character], world_data.get("characters", []))
        locations = parse_obj_as(List[Location], world_data.get("locations", []))
        
        player_character = next((c for c in characters if c.role.lower() == "player"), characters[0] if characters else None)
        starting_location = locations[0] if locations else None
        
        if not player_character or not starting_location:
            raise ValueError("Could not find player character or starting location in world data")
        
        return await generate_introduction(world_data, player_character, starting_location, True, llm_service)


async def from_json_string(json_string: str, llm_service: Optional[LLMService] = None) -> IntroductionOutput:
    """
    Generate an introduction from a JSON string.
    
    Args:
        json_string: JSON string with world data
        llm_service: Optional LLMService instance
        
    Returns:
        IntroductionOutput instance
    """
    world_data = json.loads(json_string)
    
    from app.schemas.world_generation import Character, Location, ChapterOutput
    from pydantic import parse_obj_as
    
    # Try to parse as ChapterOutput if possible
    try:
        chapter_data = parse_obj_as(ChapterOutput, world_data)
        
        # Extract world, a character and a location from the chapter data
        world_data = world_data  # Use raw dict as it may contain conflict data not in the World model
        player_character = next((c for c in chapter_data.characters if c.role.lower() == "player"), chapter_data.characters[0] if chapter_data.characters else None)
        starting_location = chapter_data.locations[0] if chapter_data.locations else None
        
        if not player_character or not starting_location:
            raise ValueError("Could not find player character or starting location in world data")
        
        return await generate_introduction(world_data, player_character, starting_location, True, llm_service)
    except Exception as e:
        logger.warning(f"Failed to parse as ChapterOutput: {str(e)}")
        
        # Fall back to manual extraction
        characters = parse_obj_as(List[Character], world_data.get("characters", []))
        locations = parse_obj_as(List[Location], world_data.get("locations", []))
        
        player_character = next((c for c in characters if c.role.lower() == "player"), characters[0] if characters else None)
        starting_location = locations[0] if locations else None
        
        if not player_character or not starting_location:
            raise ValueError("Could not find player character or starting location in world data")
        
        return await generate_introduction(world_data, player_character, starting_location, True, llm_service) 