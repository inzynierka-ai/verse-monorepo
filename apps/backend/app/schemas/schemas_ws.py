from typing import Literal, Dict, Any, Optional, Union, List
from pydantic import BaseModel, Field

# Player Character model
class PlayerCharacter(BaseModel):
    name: str = Field(..., description="Name of the player character")
    age: int = Field(..., description="Age of the player character")
    appearance: str = Field(..., description="Physical appearance description")
    background: str = Field(..., description="Background story or history")

# World Settings model
class WorldInfo(BaseModel):
    theme: str = Field(..., description="Primary theme of the world")
    genre: str = Field(..., description="Genre of the setting (fantasy, sci-fi, etc.)")
    year: int = Field(..., description="Year or time period")
    setting: str = Field(..., description="General setting description")

# Input model for world generation
class WorldGenerationInput(BaseModel):
    world: WorldInfo
    playerCharacter: Optional[PlayerCharacter] = None

# Client messages
class WorldGenerationRequest(BaseModel):
    type: Literal["generate_world"]
    world: WorldInfo
    playerCharacter: Optional[PlayerCharacter] = None

# Base message class
class WebSocketMessage(BaseModel):
    type: str

# Step update messages
class StepUpdate(WebSocketMessage):
    step: str
    message: str
    progress: float  # 0-1
    data: Optional[Dict[str, Any]] = None

# Completion messages
class WorldTemplateComplete(WebSocketMessage):
    data: Dict[str, Any]

class ChapterComplete(WebSocketMessage):
    data: Dict[str, Any]

class CharactersComplete(WebSocketMessage):
    data: Dict[str, Any]

class LocationsComplete(WebSocketMessage):
    data: Dict[str, Any]

class ConflictComplete(WebSocketMessage):
    data: Dict[str, Any]

class PossibleEndingsComplete(WebSocketMessage):
    data: Dict[str, Any]

class WorldComplete(WebSocketMessage):
    data: Dict[str, Any]

# Image prompt update
class ImagePromptUpdate(WebSocketMessage):
    entity_type: Literal["character", "location"]
    entity_id: str
    prompt: str

# Narration updates
class NarrationUpdate(WebSocketMessage):
    step: str
    content: str

class NarrationComplete(WebSocketMessage):
    data: Dict[str, Any]

# Error messages
class ErrorMessage(WebSocketMessage):
    message: str
    details: Optional[str] = None

# Union type for all possible server messages
ServerMessage = Union[
    StepUpdate, 
    WorldTemplateComplete,
    CharactersComplete,
    LocationsComplete,
    ConflictComplete,
    WorldComplete,
    NarrationUpdate,
    NarrationComplete,
    ErrorMessage
] 