from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from pydantic import BaseModel
from app.schemas.message import Message
from app.schemas.character import Character
from app.schemas.location import Location

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
    summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

