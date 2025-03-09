from typing import Literal, Dict, Any, Optional, Union
from pydantic import BaseModel

# Client messages
class WorldGenerationRequest(BaseModel):
    type: Literal["generate_world"]
    description: str
    settings: Optional[Dict[str, Any]] = None

# Server messages
class StepUpdate(BaseModel):
    type: Literal["step_update"]
    step: str
    message: str
    progress: float  # 0-1
    data: Optional[Dict[str, Any]] = None

class WorldTemplateComplete(BaseModel):
    type: Literal["world_template_complete"] 
    data: Dict[str, Any]

class CharactersComplete(BaseModel):
    type: Literal["characters_complete"]
    data: Dict[str, Any]

class LocationsComplete(BaseModel):
    type: Literal["locations_complete"] 
    data: Dict[str, Any]

class ConflictComplete(BaseModel):
    type: Literal["conflict_complete"]
    data: Dict[str, Any]

class WorldComplete(BaseModel):
    type: Literal["world_complete"]
    data: Dict[str, Any]

class NarrationUpdate(BaseModel):
    type: Literal["narration_update"]
    step: str
    content: str

class NarrationComplete(BaseModel):
    type: Literal["narration_complete"]
    data: Dict[str, Any]

class ErrorMessage(BaseModel):
    type: Literal["error"]
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