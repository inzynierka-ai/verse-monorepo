from pydantic import BaseModel, ConfigDict
from typing import Optional


class StoryBase(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    rules: Optional[str] = None
    uuid: str


class StoryCreate(BaseModel):
    title: str
    description: Optional[str] = None
    rules: Optional[str] = None


class StoryRead(StoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
