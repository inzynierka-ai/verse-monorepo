from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.character import PlayerCharacterRead


class StoryBase(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    brief_description: Optional[str] = None
    rules: Optional[str] = None
    uuid: str


class StoryCreate(BaseModel):
    title: str
    description: Optional[str] = None
    rules: Optional[str] = None


class StoryRead(StoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StoryWithPlayerCharacterRead(StoryRead):
    player_character: Optional[PlayerCharacterRead] = None
