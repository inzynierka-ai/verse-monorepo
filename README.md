# Verse: AI-Driven Text Adventure

## Overview

The game is an AI-driven, text-based adventure that showcases today's AI capabilities by creating an engaging and dynamic narrative with simple mechanics. The main goal is to build relationships with AI characters, who remember interactions and adapt based on player choices.

### Goals

-   **Player Interaction with Characters**: Players can chat with AI-generated characters, building relationships and influencing NPC attitudes through dialogue choices. NPCs will remember interactions, creating a sense of personality and consistency over time. The player's choices drive the story forward in an endless, relationship-centered narrative.
-   **Adaptive World Creation**: At the start, the player chooses or defines a setting, such as a spaceship, medieval times, or a school. The AI then tailors the world, NPC attitudes, and visuals to fit this theme. Stories contain scenes that are generated one after another, creating an endless narrative. As players progress, the AI dynamically introduces new locations, characters, and story elements, keeping gameplay fresh and engaging. The tone will adjust to the selected environment—for example, a school setting might feel lighthearted, while a murder mystery might be darker and more suspenseful. This adaptive tone provides a unique experience based on the player's chosen world.

## Technology & Mechanics

### World Generation

-   At the start of the game, the user can choose a world for the game. Based on that choice, the first characters and locations are created in a style that matches the world.
-   The introduction embeds the player in the story, showing characters and the current state of the game.

### Core AI Services

The game's narrative and state are managed by several core AI services. These include:
-   A `SceneGenerator` for creating new game situations, dynamically introducing new locations to advance the story, and creating new characters as needed to deepen the narrative.
-   A `MemoryManager` for enabling characters to remember past interactions.
-   A `ConversationService` to facilitate realistic dialogue between the player and NPCs.

These services work together to provide context to NPCs and manage the evolving game state, creating an endless narrative through a series of generated scenes.

### Web-Based Interface

-   **Simple Website**: The game features a minimalist design with a background representing the current location and a chatbox for text input, showing current conversation.

### Visuals and Atmosphere

-   Using ComfyUI, generated images will represent backgrounds and avatars that match the player-selected environment, adding immersion without complicating the interface.


## Project Structure

```
verse/
├── apps/
│   ├── frontend/ - React/TypeScript frontend using Vite
│   └── backend/ - FastAPI Python backend
├── docker-compose.yml - Docker configuration for all services
└── README.md - This file
```

## Prerequisites

To run this project, you need to have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## Running the Project

The entire application can be run with a single command using Docker Compose:

```bash
docker-compose up -d
```

This will:
1. Build and start the frontend application
2. Build and start the backend API
3. Start a PostgreSQL database

### Accessing the Services

Once all containers are running, you can access:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs - Interactive Swagger UI to explore and test the API
- **PostgreSQL Database**: 
  - Host: localhost
  - Port: 5432
  - Username: postgres
  - Password: postgres
  - Database: verse

### Viewing Logs

To view logs from all services:

```bash
docker-compose logs
```

Or for a specific service:

```bash
docker-compose logs frontend
docker-compose logs backend
docker-compose logs db
```

### Stopping the Project

To stop all running containers:

```bash
docker-compose down
```

To stop and remove all data (including the database volume):

```bash
docker-compose down -v
```

## Development

### Rebuilding After Changes

If you make changes to the code, rebuild the containers:

```bash
docker-compose build
docker-compose up -d
```

## Troubleshooting

- If you encounter port conflicts, ensure ports 5173, 8000, and 5432 are not in use by other applications.
- Check logs for specific errors: `docker-compose logs [service_name]`
