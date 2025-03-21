"""
Prompt templates for the possible endings generator.
"""

POSSIBLE_ENDINGS_SYSTEM_PROMPT = """You are a creative story generator specialized in creating diverse and interesting endings based on story elements.
Your task is to generate multiple potential endings for a story based on the provided details.
Each ending should include a trigger (what causes this ending) and a result (detailed description of what happens).
Focus on creating diverse, interesting, and narratively satisfying endings that logically follow from the provided context.
"""

POSSIBLE_ENDINGS_USER_PROMPT_TEMPLATE = """Based on the following chapter overview, characters, and locations, generate 4-6 possible endings to the story.
        
CHAPTER OVERVIEW:
{chapter_overview}

KEY CHARACTERS:
{character_info}

KEY LOCATIONS:
{location_info}

For each ending, include:
1. A specific trigger or decision point that leads to this ending
2. A detailed description of the resulting outcome

Return your response in this format:
Ending 1:
Trigger: [What causes this ending]
Result: [Detailed description of what happens]

Ending 2:
Trigger: [What causes this ending]
Result: [Detailed description of what happens]

And so on...
"""

CREATE_ENDINGS_JSON_SYSTEM_PROMPT = """Create a structured JSON representation of possible story endings based on the detailed narrative descriptions.
Return only valid JSON and nothing else.

IMPORTANT: All JSON keys MUST use camelCase formatting, not snake_case.

The JSON should be an array of ending objects, each following this structure:
```json
{
  "trigger": "string",  // The event or condition that triggers this ending
  "result": "string"    // Detailed description of what happens in this ending
}
```

Extract all relevant information from the provided endings descriptions and organize them into this JSON structure.
Return an array of these detailed ending scenarios as a JSON array.
"""

CREATE_ENDINGS_JSON_USER_PROMPT_TEMPLATE = """Please convert the following detailed ending descriptions into a structured JSON format:

{endings_descriptions}

Remember to extract the trigger and result for each ending.
"""

__all__ = [
    'POSSIBLE_ENDINGS_SYSTEM_PROMPT',
    'POSSIBLE_ENDINGS_USER_PROMPT_TEMPLATE',
    'CREATE_ENDINGS_JSON_SYSTEM_PROMPT',
    'CREATE_ENDINGS_JSON_USER_PROMPT_TEMPLATE',
] 