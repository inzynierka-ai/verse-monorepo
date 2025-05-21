---
config:
  theme: default
---
flowchart TD
 subgraph subGraph0["Initial Setup"]
    direction LR
        SG["StoryGenerator: Generate Story"]
        B{"Player Chooses/Defines World Setting"}
        PCG["CharacterGenerator: Generate Player Character"]
  end
 subgraph SceneGenerationAndDisplay["SceneGenerationAndDisplay"]
    direction TB
        SceneGen["SceneGenerator: Initiate Scene"]
        BeginSceneLoop["Scene Loop Start"]
        LG["LocationGenerator: Manage Location"]
        NPC_CG["CharacterGenerator: Manage NPCs for Scene"]
        SceneDetails["SceneDetails"]
        SceneGen_Describe["SceneGenerator: Describe Scene Content"]
        UI_DisplayScene["UI: Display Scene to Player"]
  end
 subgraph InteractionCycle["InteractionCycle"]
    direction TB
        Mod_Input["ModerationService: Moderate Player Input"]
        PlayerInteractionLoop{"Player Interacts (sends message)"}
        CS["ConversationService: Process Player Message"]
        MM_Retrieve["MemoryManager: Retrieve Relevant NPC Memories"]
        WES_Retrieve["WorldEntityService: Retrieve Relevant World Entities/Lore"]
        CS_NPCResponse["ConversationService: Generate NPC Response - LLM"]
        Mod_Output["ModerationService: Moderate NPC Response"]
        UI_DisplayResponse["UI: Display NPC Response"]
  end
 subgraph PostInteractionProcessing["PostInteractionProcessing"]
    direction TB
        MM_Save["MemoryManager: Save New Interaction to NPC Memory"]
        PostInteractionProcessing_Entry["Entry"]
        RA["RelationshipAnalysisService: Analyze & Update Player-NPC Relationship"]
        WES_Process["WorldEntityService: Extract & Define New World Entities from Conversation"]
  end
    A["Start Game"] --> B
    B --> SG
    SG --> PCG
    PCG --> BeginSceneLoop
    BeginSceneLoop --> SceneGen
    SceneGen -- Generates/Selects --> LG & NPC_CG
    LG --> SceneDetails
    NPC_CG --> SceneDetails
    SceneDetails --> SceneGen_Describe
    SceneGen_Describe --> UI_DisplayScene
    UI_DisplayScene --> PlayerInteractionLoop
    PlayerInteractionLoop --> Mod_Input
    Mod_Input -- Input OK --> CS
    Mod_Input -- Input Flagged --> PlayerInteractionLoop
    CS -- Retrieves Context --> MM_Retrieve & WES_Retrieve
    MM_Retrieve --> CS_NPCResponse
    WES_Retrieve --> CS_NPCResponse
    CS_NPCResponse --> Mod_Output
    Mod_Output -- Response OK --> UI_DisplayResponse
    Mod_Output -- Response Flagged --> CS_NPCResponse
    UI_DisplayResponse --> PostInteractionProcessing
    PostInteractionProcessing_Entry --> MM_Save
    MM_Save --> RA
    RA --> WES_Process
    WES_Process --> SceneGen_Evaluate["SceneGenerator: Evaluate Scene State"]
    SceneGen_Evaluate -- Continue Current Scene --> PlayerInteractionLoop
    SceneGen_Evaluate -- New Scene Needed --> BeginSceneLoop
     SG:::service
     PCG:::service
     SceneGen:::service
     LG:::service
     NPC_CG:::service
     Mod_Input:::service
     CS:::service
     MM_Retrieve:::service
     WES_Retrieve:::service
     CS_NPCResponse:::service
     Mod_Output:::service
     MM_Save:::service
     RA:::service
     WES_Process:::service
     SceneGen_Evaluate:::service
    classDef service fill:#cde4ff,stroke:#333,stroke-width:2px,color:#000
