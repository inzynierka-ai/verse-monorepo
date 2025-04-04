
# Game WebSocket System

This document describes the WebSocket-based communication system used for the Verse game backend.

## Overview

The game uses WebSockets for real-time bidirectional communication between the client and server. The system is built with FastAPI and provides a flexible, extensible architecture for handling various message types.

## Architecture

1. **WebSocket Endpoint**: `/ws/game` - Main connection point for game clients
2. **Message Handler**: Central handler that routes messages to specialized handlers
3. **Handler System**: Modular system of handlers that process specific message types

## Connection Lifecycle

1. Client connects to the WebSocket endpoint
2. Server accepts connection and tracks it
3. Client sends JSON messages with a specific type and payload
4. Server routes messages to appropriate handlers
5. Handler processes message and sends response(s)
6. When client disconnects, connection is removed from tracking

## Message Format

All messages follow this JSON format:

```json
{
  "type": "MESSAGE_TYPE",
  "payload": {
    // Message-specific data
  }
}
```

## Client -> Server Message Types

### INITIALIZE_GAME

Initializes a new game world and character.

**Payload**:
```json
{
  "world": {
    "theme": "String - emotional/philosophical concept",
    "genre": "String - storytelling style",
    "year": "Integer - time period",
    "setting": "String - physical environment"
  },
  "playerCharacter": {
    "name": "String - character name",
    "age": "Integer - character age",
    "appearance": "String - character appearance",
    "background": "String - character backstory"
  }
}
```

## Server -> Client Message Types

### STATUS_UPDATE

Provides status updates during processing.

**Payload**:
```json
{
  "status": "String - status code",
  "message": "String - human-readable message"
}
```

**Status codes include**:
- `GENERATING_WORLD`
- `GENERATING_CHARACTER`

### WORLD_CREATED

Sent when the world has been generated.

**Payload**:
```json
{
  "description": "String - detailed world description",
  "rules": ["String - world rule 1", "String - world rule 2", ...]
}
```

### CHARACTER_CREATED

Sent when the player character has been created.

**Payload**:
```json
{
  "name": "String - character name",
  "description": "String - detailed character description",
  "personalityTraits": ["String - trait 1", "String - trait 2", ...],
  "backstory": "String - character's backstory",
  "goals": ["String - goal 1", "String - goal 2", ...],
  "relationships": [
    {
      "name": "String - related character name",
      "level": "Integer - relationship strength",
      "type": "String - relationship type",
      "backstory": "String - relationship backstory"
    },
    ...
  ],
  "imagePrompt": "String - image generation prompt",
  "role": "player | npc"
}
```

### INITIALIZATION_COMPLETE

Sent when the game initialization process is complete.

**Payload**:
```json
{
  "message": "String - completion message"
}
```

### ERROR

Sent when an error occurs during processing.

**Payload**:
```json
{
  "message": "String - error message",
  "details": "Optional - additional error details"
}
```

## Error Handling

The system has multiple layers of error handling:
1. JSON parsing errors (invalid JSON)
2. Message validation errors (missing type, invalid payload)
3. Handler-specific errors (validation errors, processing errors)
4. Unexpected errors (server errors, connection issues)

## Extending the System

New message types can be added by:
1. Creating a new handler class that extends `BaseMessageHandler`
2. Implementing the `handle` method to process specific message types
3. Adding the handler to the `GameMessageHandler` instance 