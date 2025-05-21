sequenceDiagram
    participant Client
    participant StoriesRouter as StoriesRouter
    participant MemoryManager
    participant SceneService
    participant RelationshipAnalysisService
    participant DB as Database

    Client->>StoriesRouter: PATCH /complete
    
    StoriesRouter->>DB: get_story(story_uuid, user_id)
    DB-->>StoriesRouter: story
    
    StoriesRouter->>MemoryManager: create_memories(db, scene_uuid)
    MemoryManager->>DB: Query Scene & Characters
    DB-->>MemoryManager: scene with characters
    
    loop For each character
        MemoryManager->>DB: get_messages_by_scene_and_character
        DB-->>MemoryManager: messages
        MemoryManager->>MemoryManager: create_memory_chunks
        MemoryManager->>DB: save_memory(character_id, scene_id, text)
        DB-->>MemoryManager: memory_id
    end
    MemoryManager-->>StoriesRouter: memories_created
    
    StoriesRouter->>DB: get_scene_by_uuid(scene_uuid)
    DB-->>StoriesRouter: scene with messages
    
    StoriesRouter->>RelationshipAnalysisService: analyze_relationship(character_id, messages)
    
    loop For each character in scene
        RelationshipAnalysisService->>DB: get_character(character_id)
        DB-->>RelationshipAnalysisService: character
        RelationshipAnalysisService->>RelationshipAnalysisService: _format_messages_for_analysis
        RelationshipAnalysisService->>RelationshipAnalysisService: _generate_relationship_analysis
        RelationshipAnalysisService->>RelationshipAnalysisService: _extract_relationship_level
        RelationshipAnalysisService->>DB: Update character.relationship_level
        DB-->>RelationshipAnalysisService: Updated character
        RelationshipAnalysisService-->>StoriesRouter: relationship_result
    end
    
    StoriesRouter->>SceneService: mark_scene_completed(db, scene_uuid, story_id)
    SceneService->>DB: mark_scene_as_completed
    DB-->>SceneService: completed_scene
    SceneService->>SceneService: process_completed_scene
    SceneService->>DB: update_scene_summary
    DB-->>SceneService: updated_scene
    SceneService-->>StoriesRouter: completed_scene
    
    StoriesRouter-->>Client: {"message": "Scene completed successfully"}