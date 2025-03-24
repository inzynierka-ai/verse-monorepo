"""
Prompt templates for the Narrator agent.
"""

# System prompts
NARRATOR_SYSTEM_PROMPT = """You are a master storyteller creating an immersive introduction for a narrative game. 
Your task is to craft evocative, engaging prose that draws players into the world.
Write in second person perspective where appropriate.
Aim for 3-4 sentences that paint a vivid picture and establish the right tone.
Focus on sensory details, emotional resonance, and creating intrigue.
Avoid exposition dumps or overwhelming details.
Create text that would appear during a game's opening sequence."""

# Setting establishment prompt templates
SETTING_PROMPT_TEMPLATE = """Create an immersive introduction to the game world that establishes the setting, time period, and atmosphere.

WORLD SETTING:
{setting_summary}

WORLD RULES:
{rules_text}

Write 3-4 evocative sentences that introduce players to this world, focusing on what makes it unique, 
interesting, and atmospheric. End with a sense of tension or possibility that draws the player in.
"""

# Character introduction prompt templates
CHARACTER_PROMPT_TEMPLATE = """Create an introduction to the player character that makes them feel embodied in the role.

CHARACTER NAME: {name}

DESCRIPTION:
{description}

BACKSTORY:
{backstory}

PERSONALITY TRAITS:
{traits_text}

GOALS:
{goals_text}

Write 3-4 sentences in second-person perspective that introduce the player to their character,
focusing on who they are, what motivates them, and what makes them unique.
Make the player feel connected to this character.
"""

# Conflict glimpse prompt templates
CONFLICT_PROMPT_TEMPLATE = """Create a glimpse of the central conflict that will drive the narrative.

CONFLICT TITLE: {title}

DESCRIPTION:
{description}

KEY FACTIONS:
{factions_text}

PERSONAL STAKES:
{personal_stakes}

WORLD STAKES:
{world_stakes}

Write 3-4 sentences that introduce the central conflict, creating intrigue and tension.
Focus on what's at stake, the opposing forces, and why this matters to the player character.
Create a sense of urgency without revealing everything.
"""

# Location focus prompt templates
LOCATION_PROMPT_TEMPLATE = """Create a vivid description of the player's starting location.

LOCATION NAME: {name}

DESCRIPTION:
{description}

ATMOSPHERE:
{atmosphere}

KEY ELEMENTS:
{elements_text}

Write 3-4 sentences that establish the player's immediate surroundings in second-person perspective.
Focus on sensory details (sights, sounds, smells, etc.) that make the location feel real and present.
Create a strong sense of place and hint at what the player might discover or interact with.
"""

# Call to action prompt templates
CALL_TO_ACTION_PROMPT_TEMPLATE = """Create a compelling call to action that sets the player on their journey.

PRIMARY GOAL: {first_goal}

POTENTIAL STORY HOOKS:
{hooks_text}

POSSIBLE PATHS:
{resolutions_text}

Write 3-4 sentences that motivate the player to begin their adventure.
Focus on their immediate objective, the sense of possibility ahead, and why their choices matter.
End with a powerful statement that propels them forward into the game world.
""" 