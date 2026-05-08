---
config:
  theme: default
---
sequenceDiagram
    participant Client
    participant LocationGenerator
    participant LLMService
    participant JSONService
    participant ComfyUIService
    participant Database

    Client->>LocationGenerator: generate_location(story, description)
    Note over LocationGenerator: Generate UUID

    LocationGenerator->>LLMService: _describe_location(story, description, UUID)
    LLMService-->>LocationGenerator: location_description

    LocationGenerator->>LLMService: _create_location_json(location_description, UUID)
    LLMService-->>LocationGenerator: response_text
    LocationGenerator->>JSONService: parse_and_validate_json_response(response_text)
    JSONService-->>LocationGenerator: location_from_llm (structured data)

    LocationGenerator->>LLMService: _generate_image_prompt(location_from_llm, story_description, UUID)
    LLMService-->>LocationGenerator: image_prompt

    LocationGenerator->>ComfyUIService: _generate_image(image_prompt)
    Note over ComfyUIService: Asynchronous image generation
    ComfyUIService-->>LocationGenerator: image_url

    LocationGenerator->>LocationGenerator: Create final Location object

    
    LocationGenerator->>Database: _save_location_to_db(location, story_id, image_prompt)
    Database-->>LocationGenerator: db_location
    

    LocationGenerator-->>Client: location (complete with image URL)