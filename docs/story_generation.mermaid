---
config:
  theme: default
---
sequenceDiagram
    participant User
    participant GameInitializer
    participant StoryGenerator
    participant ModerationsService
    participant LLMService
    participant CharacterGenerator
    participant Database

    User->>GameInitializer: initialize_game(StoryGenerationInput)
    
    %% Story Generation Process
    GameInitializer->>StoryGenerator: generate_story(user_id, input)
    StoryGenerator->>ModerationsService: process_moderation(input)
    
    alt Content violates moderation
        ModerationsService-->>StoryGenerator: Return violated categories
        StoryGenerator-->>GameInitializer: Raise ValueError
        GameInitializer-->>User: Error: Content not allowed
    else Content passes moderation
        ModerationsService-->>StoryGenerator: Return None (passed)
        
        StoryGenerator->>LLMService: generate_completion (story description)
        LLMService-->>StoryGenerator: Return story description
        
        StoryGenerator->>LLMService: generate_completion (story details)
        LLMService-->>StoryGenerator: Return story details (title, brief, rules)
        
        StoryGenerator->>StoryGenerator: Generate UUID
        
        opt Database session available
            StoryGenerator->>Database: Save story to database
            Database-->>StoryGenerator: Return story ID
        end
        
        StoryGenerator-->>GameInitializer: Return Story object
        
        opt Callback provided
            GameInitializer->>User: on_story_generated(story)
        end
        
        %% Character Generation Process
        GameInitializer->>CharacterGenerator: generate_character(playerCharacter, story, is_player=True)
        Note over CharacterGenerator: Uses story context for character generation
        CharacterGenerator-->>GameInitializer: Return Character object
        
        opt Callback provided
            GameInitializer->>User: on_character_generated(character)
        end
        
        GameInitializer->>GameInitializer: Create InitialGameState
        GameInitializer-->>User: Return InitialGameState(story, playerCharacter)
    end