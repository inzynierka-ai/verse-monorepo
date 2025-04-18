# Game Engine

This directory contains services responsible for generating and managing the game story, characters, locations, scenes, and narrative flow.

## Architecture Overview

### Tools

Located in the `tools/` directory, these are reusable components used by orchestrators:

1. **StoryGenerator**
   - Generates detailed story description and rules
   - Takes StoryInput (theme, genre, year, setting)
   - Produces complete Story object

2. **CharacterGenerator**
   - Generates detailed characters with personalities, backstories, and goals
   - Takes CharacterDraft and Story context
   - Produces Character objects with image prompts
   
3. **LocationGenerator**
   - Generates detailed locations with descriptions and features
   - Takes Story context
   - Produces Location objects with image prompts

4. **Narrator** (planned)
   - Generates natural language descriptions of scenes
   - Creates NPC dialogue and responses
   - Narrates outcomes of player actions
   - Maintains consistent tone and style throughout the game

### Orchestrators

Located in the `orchestrators/` directory, these are services that coordinate the game flow:

1. **GameInitializer**
   - Coordinates the generation of Story and Player Character
   - Takes StoryGenerationInput from the user
   - Produces InitialGameState with Story and PlayerCharacter
   - Entry point for starting a new game

2. **StoryController** (planned)
   - Maintains the game state, including:
   - Story facts and rules
   - Character relationships and memories
   - Game history and important events
   - Current narrative state
   - Provides context for the Scene Director to generate scenes

3. **SceneDirector** (planned)
   - Takes the current game state from Story Controller
   - Dynamically creates NPCs and locations as needed
   - Generates narrative goals and scene structures
   - Assembles coherent scenes for player interaction

## Implementation Flow

```
User Input → GameInitializer → StoryController → SceneDirector → Narrator → Player Interface
```

All subsequent scenes will be dynamically generated by the SceneDirector based on player choices and the evolving game state managed by the StoryController. 