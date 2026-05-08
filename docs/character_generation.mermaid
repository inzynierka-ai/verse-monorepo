---
config:
  theme: default
---
sequenceDiagram
    actor Client
    participant CharGen as CharacterGenerator
    participant LLM as LLMService
    participant JSON as JSONService
    participant ImageGen as ComfyUIService
    participant DB as Database
    Client->>CharGen: generate_character(characterDraft, story, isPlayer)
    Note over CharGen: Create UUID
    CharGen->>LLM: _describe_character()
    LLM-->>CharGen: character description
    CharGen->>LLM: _create_character_json()
    LLM-->>CharGen: JSON response
    CharGen->>JSON: parse_and_validate_json_response()
    JSON-->>CharGen: CharacterFromLLM object
    CharGen->>LLM: _generate_image_prompt()
    LLM-->>CharGen: image prompt
    CharGen->>ImageGen: _generate_image()
    ImageGen-->>CharGen: image URL
    Note over CharGen: Create Character object
    CharGen->>DB: _save_character_to_db()
    DB-->>CharGen: Saved character model
    CharGen-->>Client: Character object
