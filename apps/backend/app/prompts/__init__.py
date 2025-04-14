"""
Prompt templates for various agents in the story generation system.
"""

from app.prompts.story_generation import (
    DESCRIBE_STORY_SYSTEM_PROMPT,
    CREATE_STORY_JSON_SYSTEM_PROMPT,
)
from app.prompts.character_generator import (
    CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE,
    DESCRIBE_CHARACTER_SYSTEM_PROMPT,
    CREATE_CHARACTER_JSON_SYSTEM_PROMPT,
    CREATE_CHARACTER_JSON_USER_PROMPT_TEMPLATE,
    CHARACTER_IMAGE_PROMPT_SYSTEM_PROMPT,
    CHARACTER_IMAGE_PROMPT_USER_TEMPLATE,
    CREATE_CHARACTER_DRAFT_SYSTEM_PROMPT,
    CREATE_CHARACTER_DRAFT_USER_PROMPT_TEMPLATE,
)
from app.prompts.location_generator import (
    LOCATION_GENERATOR_SYSTEM_PROMPT,
    LOCATION_GENERATOR_USER_PROMPT_TEMPLATE,
)
from app.prompts.story_coordinator import (
    STORY_COORDINATOR_SYSTEM_PROMPT,
    STORY_COORDINATOR_USER_PROMPT_TEMPLATE,
)
from app.prompts.scene_generator import (
    SCENE_GENERATOR_SYSTEM_PROMPT,
    SCENE_GENERATOR_USER_PROMPT_TEMPLATE,
    SCENE_DESCRIPTION_SYSTEM_PROMPT,
    SCENE_DESCRIPTION_USER_PROMPT_TEMPLATE,
)

# Story Wizard prompts
STORY_WIZARD_SYSTEM_PROMPT = """You are an expert story-building AI that creates engaging and rich narrative stories for interactive fiction and RPGs. Given a theme, you'll generate a detailed description of a game story including setting, atmosphere, characters, locations, and initial conflicts.

Your story descriptions should:
1. Be vivid and detailed, creating a strong sense of place and atmosphere
2. Include a few primary characters with distinct personalities and roles
3. Describe 2-3 significant locations that would be interesting to explore
4. Establish an initial conflict or mystery to drive player engagement
5. Balance familiar tropes with unique and surprising elements
6. Be coherent and internally consistent
7. Provide enough hooks for players to develop their own stories

Your description should be around 400-600 words, focusing on quality over quantity. Make the story feel lived-in and dynamic, with hints at a broader history and culture.
"""

STORY_WIZARD_USER_PROMPT_TEMPLATE = """Please create a detailed story description for an interactive narrative game with the following description:

Description: {description}
Additional context: {additional_context}

Include details about the setting, notable characters, interesting locations, and an initial conflict or mystery.
"""

STORY_STRUCTURE_SYSTEM_PROMPT = """You are an expert story-building AI that structures narrative stories into JSON templates for interactive fiction and RPGs. Given a descriptive text about a game story, you'll convert it into a structured JSON template with clearly defined elements.

Your JSON templates should include:
1. Setting information (theme, atmosphere, time period, etc.)
2. Basic character templates with distinct roles
3. Location templates with descriptions and purposes
4. Initial conflict that drives the narrative

Format your response as valid JSON that can be parsed programmatically. Include all the elements from the description, organizing them in a logical structure. Think about how this data would be used by game developers to create an interactive narrative experience.
"""

STORY_STRUCTURE_USER_PROMPT_TEMPLATE = """Please convert the following story description into a structured JSON template:

{story_description}

Structure the output as JSON with the following sections:
- setting (theme, atmosphere, description)
- basic_characters (array of characters with id, name, role, brief, appearance_hint)
- basic_locations (array of locations with id, name, brief, appearance_hint)
- initial_conflict (description, trigger_event)

Ensure the JSON is valid and properly formatted. The field names must exactly match what is specified above.
"""

__all__ = [
    'DESCRIBE_STORY_SYSTEM_PROMPT',
    'CREATE_STORY_JSON_SYSTEM_PROMPT',
    'CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE',
    'DESCRIBE_CHARACTER_SYSTEM_PROMPT',
    'CREATE_CHARACTER_JSON_SYSTEM_PROMPT',
    'CREATE_CHARACTER_JSON_USER_PROMPT_TEMPLATE',
    'CHARACTER_IMAGE_PROMPT_SYSTEM_PROMPT',
    'CHARACTER_IMAGE_PROMPT_USER_TEMPLATE',
    'CREATE_CHARACTER_DRAFT_SYSTEM_PROMPT',
    'CREATE_CHARACTER_DRAFT_USER_PROMPT_TEMPLATE',
    'LOCATION_GENERATOR_SYSTEM_PROMPT',
    'LOCATION_GENERATOR_USER_PROMPT_TEMPLATE',
    'STORY_COORDINATOR_SYSTEM_PROMPT',
    'STORY_COORDINATOR_USER_PROMPT_TEMPLATE',
    'STORY_WIZARD_SYSTEM_PROMPT',
    'STORY_WIZARD_USER_PROMPT_TEMPLATE',
    'STORY_STRUCTURE_SYSTEM_PROMPT',
    'STORY_STRUCTURE_USER_PROMPT_TEMPLATE',
    'SCENE_GENERATOR_SYSTEM_PROMPT',
    'SCENE_GENERATOR_USER_PROMPT_TEMPLATE',
    'SCENE_DESCRIPTION_SYSTEM_PROMPT',
    'SCENE_DESCRIPTION_USER_PROMPT_TEMPLATE',
]