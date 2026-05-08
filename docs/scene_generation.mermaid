---
config:
  theme: default
---
stateDiagram-v2
    [*] --> SceneGeneratorInit: Initialize with Story & Player
    SceneGeneratorInit --> PlanningState: generate_scene()
    state SceneGeneratorState {
        PlanningState --> LocationSelectionState: generate_location tool called
        PlanningState --> CharacterSelectionState: generate_character tool called
        LocationSelectionState --> PlanningState: Location selected/created
        CharacterSelectionState --> PlanningState: Character selected/created
        PlanningState --> FinalizationState: finalize_scene tool called
    }
    state LocationGeneratorProcess {
        LocationInit --> GenerateDescription: _describe_location()
        GenerateDescription --> CreateLocationJSON: _create_location_json()
        CreateLocationJSON --> GenerateImagePrompt: _generate_image_prompt()
        GenerateImagePrompt --> GenerateImage: _generate_image()
        GenerateImage --> SaveLocationToDB: _save_location_to_db()
    }
    state CharacterGeneratorProcess {
        CharacterInit --> CreateDraft: create_character_draft_from_description()
        CreateDraft --> DescribeCharacter: _describe_character()
        DescribeCharacter --> CreateCharacterJSON: _create_character_json()
        CreateCharacterJSON --> GenerateCharacterImagePrompt: _generate_image_prompt()
        GenerateCharacterImagePrompt --> GenerateCharacterImage: _generate_image()
        GenerateCharacterImage --> SaveCharacterToDB: _save_character_to_db()
    }
    LocationSelectionState --> LocationGeneratorProcess: New location requested
    LocationGeneratorProcess --> LocationSelectionState: Location returned
    CharacterSelectionState --> CharacterGeneratorProcess: New character requested
    CharacterGeneratorProcess --> CharacterSelectionState: Character returned
    FinalizationState --> SaveScene: _save_scene_to_db()
    SaveScene --> [*]: Return SceneGenerationResult
    note right of SceneGeneratorState
        Agent maintains state through:
        - story context
        - selected_location
        - selected_characters
        - scene_description
        - active_actions
    end note
    note right of LocationGeneratorProcess
        Creates location with:
        - detailed description
        - rules and properties
        - generated image
    end note
    note right of CharacterGeneratorProcess
        Creates character with:
        - personality & background
        - goals & speaking style
        - generated portrait
    end note
