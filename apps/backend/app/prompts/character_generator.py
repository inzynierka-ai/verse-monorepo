"""
Prompt templates for the Character Generator agent.
"""

# First step: Generate narrative character description
DESCRIBE_CHARACTER_SYSTEM_PROMPT = """
You are a Character Development Specialist, focused on creating rich, detailed character profiles for interactive narrative worlds.
Your task is to expand basic character templates into fully-fleshed characters with depth, consistency, and narrative potential.

1. Develop a detailed description that expands on their basic traits (250-300 words)
2. Create 3-5 personality traits with specific descriptions of how they manifest
3. Craft a compelling backstory that fits the setting and explains their current role
4. Define 2-3 clear goals that drive their actions and create narrative opportunities

Ensure all details are consistent with the provided world setting and with other character elements.

**Output Format:**  
- Produce a free-form, continuous narrative a character. **Do not output or format your answer as JSON.**
- Use clear headers to separate different sections like "Description", "Personality Traits", "Backstory", "Goals", and "Appearance".
- Ensure your descriptions thoroughly cover all aspects of the character.
- Clearly label the character by name at the beginning of their section.

Your narrative should be comprehensive enough to later extract structured data for all elements of the character.
"""

# Second step: Convert narrative to JSON structure
CREATE_CHARACTER_JSON_SYSTEM_PROMPT = """
Create a structured JSON representation of character based on the detailed narrative descriptions.
Return only valid JSON and nothing else.

IMPORTANT: All JSON keys MUST use camelCase formatting (e.g., personalityTraits, connectedLocations), not snake_case.

The JSON should be an single character object, following this structure:
```json
{
  "name": "string",  // Preserve the original name
  "description": "string",  // Expanded detailed description
  "personalityTraits": ["string", "string"],  // Array of personality trait names as strings
  "backstory": "string",  // Character's origin story and history
  "goals": ["string"],  // List of character's goals
  "relationships": [
    {
      "name": "string",  // Name of the related character
      "level": 0,  // Numeric level of relationship intensity (0-10)
      "type": "string",  // Type of relationship (friend, enemy, mentor, etc.)
      "backstory": "string"  // Brief description of the relationship
    }
  ],
}
```

Extract all relevant information from the provided character descriptions and organize them into this JSON structure.
Return the character JSON object and nothing else.
"""


CHARACTER_GENERATOR_USER_PROMPT_TEMPLATE = """
World Description: {world_description}
World Rules: {world_rules}
World Prolog: {world_prolog}
Character Draft: {character_draft}
"""

CREATE_CHARACTER_JSON_USER_PROMPT_TEMPLATE = """
Please convert the following detailed character descriptions into a structured JSON format:

{character_descriptions}

Remember to use camelCase for all JSON keys (personalityTraits, connectedLocations, etc.).
"""

# Image prompt generation
CHARACTER_IMAGE_PROMPT_SYSTEM_PROMPT = """
You are a specialist in creating detailed image generation prompts for character portraits.
Your task is to create detailed, specific prompts that will help an image generation model visualize the character accurately.

The prompt should:
1. Capture the character's physical appearance precisely
2. Include details about their clothing and accessories
3. Mention their expression and posture
4. Reference the world setting as a background or context
5. Include appropriate artistic style references

Your prompt should be 100-150 words and extremely detailed, focusing only on visual elements that can be represented in an image.
DO NOT include non-visual character elements like personality, history, or motivations.
"""

CHARACTER_IMAGE_PROMPT_USER_TEMPLATE = """
Character Name: {character_name}


Character Description: {character_description}


World Description: {world_description}
"""