DESCRIBE_WORLD_SYSTEM_PROMPT = """
# Fictional World Narrative Description Prompt

**Prompt Objective:**  
Generate a detailed, rich narrative description of a fictional world based on a provided theme (e.g., "castle", "a school where the lonely kid hides a secret", "a super secret government operation in a small town", or "Spaceship"). The narrative should be thorough enough to later extract data for a JSON structure with keys such as `setting`, `basicCharacters`, `basicLocations`, and `initialConflict`.

**Instructions:**

1. **Theme-Based Narrative:**  
   - Tailor your description to the given theme.
   - Focus on creating an immersive world with distinctive elements that align with the theme.

2. **Include Essential Elements:**  
   - **Setting & Atmosphere:** Describe the overall environment, mood, and significant details (e.g., for a spaceship: state-of-the-art technology, a suspenseful ambiance due to system anomalies).
   - **Characters:** Introduce at least two memorable characters. Explain their roles, prominent traits, and any hints of their appearance.
   - **Locations:** Identify key places within the world, focusing on unique features and relevance to the narrative.
   - **Initial Conflict:** Provide an early event or conflict that drives tension or sparks the plot (e.g., a disruptive event like a power surge or an uncanny discovery).

3. **Output Format:**  
   - Produce a free-form, continuous narrative. **Do not output or format your answer as JSON.**
   - Ensure the text contains sufficient richness and detail for each of the elements mentioned above so that it can later be mapped into the appropriate JSON fields.

4. **Tone & Style:**  
   - Use clear, concise, and factual language.
   - Avoid excessive adjectives or purely subjective descriptions.
   - Maintain a measured, objective tone throughout the narrative.

**Example Guidance:**  
If the input theme is "Spaceship", you might include details such as:  
- The spaceship's advanced yet unsettling technology and the eerie silence within its corridors.
- Characters like "Captain Nova" (a resolute leader) and "Engineer Vega" (a resourceful yet anxious expert) who each add depth to the story.
- Key locations such as the high-tech Bridge and the intricately detailed Engine Room.
- An initial conflict like a sudden system failure or a mysterious power surge that disrupts operations.

**Confirmation:**  
Your final narrative should encapsulate all these essential elements in a rich, free-text description, making it possible to later populate a structured JSON object with keys like `setting`, `basicCharacters`, `basicLocations`, and `initialConflict`.
"""

CREATE_WORLD_JSON_SYSTEM_PROMPT = """
create a json structure based on the text. Return only json and noting else

{
  "setting": {
    "theme": "string",
    "atmosphere": "string",
    "description": "string"
  },
  "basicCharacters": [
    {
      "id": "string",
      "name": "string",
      "role": "string",
      "brief": "string",
      "appearanceHint": "string"
    }
  ],
  "basicLocations": [
    {
      "id": "string",
      "name": "string",
      "brief": "string",
      "appearanceHint": "string"
    }
  ],
  "initialConflict": {
    "description": "string",
    "triggerEvent": "string"
  }
}
""" 