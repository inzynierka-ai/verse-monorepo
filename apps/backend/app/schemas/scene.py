from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

from pydantic import BaseModel
from app.schemas.message import Message
from app.schemas.character import Character
from app.schemas.location import Location

class SceneSummaryBase(BaseModel):
    total_messages: int
    character_participation: Dict[str, int]
    key_events: List[Any]
    sentiment: Dict[str, Any]
    relationships: Dict[str, Any]

class SceneSummary(SceneSummaryBase):
    id: int
    scene_id: int
    
    model_config = ConfigDict(from_attributes=True)

class Scene(BaseModel):
    id: int
    description: str
    location_id: int
    story_id: int
    uuid: str
    status: str
    location: Location
    characters: List[Character]
    messages: List[Message]
    summary: Optional[SceneSummary] = None

    model_config = ConfigDict(from_attributes=True)

