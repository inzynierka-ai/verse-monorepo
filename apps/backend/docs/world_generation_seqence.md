sequenceDiagram
    participant Client
    participant API as WebSocket API
    participant Coordinator as WorldGenerationCoordinator
    participant Wizard as WorldWizard
    participant CharGen as Character Generator
    participant LocGen as Location Generator
    participant ConflictGen as Conflict Generator
    participant WorldGen as World Generator
    participant Narrator as Narrator
    
    Client->>API: Connect to WebSocket
    Client->>API: Send WorldGenerationRequest
    API->>Coordinator: Forward request
    
    %% Step 1: World Wizard
    Coordinator->>API: Send step_update (world_template)
    Coordinator->>Wizard: create_world_template()
    Wizard-->>Coordinator: Return WorldTemplate
    Coordinator->>API: Send world_template_complete
    
    %% Step 2: Characters and Locations (parallel)
    Coordinator->>API: Send step_update (characters_and_locations)
    
    par Characters Generation
        Coordinator->>CharGen: generate_characters()
        CharGen-->>Coordinator: Return DetailedCharacters
        Coordinator->>API: Send characters_complete
    and Locations Generation
        Coordinator->>LocGen: generate_locations()
        LocGen-->>Coordinator: Return DetailedLocations
        Coordinator->>API: Send locations_complete
    end
    
    %% Step 3: Conflict Generation
    Coordinator->>API: Send step_update (conflict)
    Coordinator->>ConflictGen: generate_conflict()
    ConflictGen-->>Coordinator: Return DetailedConflict
    Coordinator->>API: Send conflict_complete
    
    %% Step 4: World Integration
    Coordinator->>API: Send step_update (world_integration)
    Coordinator->>WorldGen: integrate_world_components()
    WorldGen-->>Coordinator: Return FinalGameWorld
    Coordinator->>API: Send world_complete
    
    %% Step 5: Narration
    Coordinator->>API: Send step_update (narration)
    Coordinator->>Narrator: generate_introduction()
    
    loop For each narration step
        Narrator-->>Coordinator: Return narration step
        Coordinator->>API: Send narration_update
    end
    
    Coordinator->>API: Send narration_complete
    API-->>Client: Deliver all updates