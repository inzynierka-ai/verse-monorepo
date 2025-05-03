from typing import List
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
    location: Location
    characters: List[Character]
    messages: List[Message]
    description: str

    model_config = ConfigDict(from_attributes=True)

