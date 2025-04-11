from pydantic import BaseModel, ConfigDict
from typing import Optional

class StoryBase(BaseModel):
    user_id: int
    title: str
    description: str
    rules: Optional[str] = None
    uuid: str

class StoryCreate(BaseModel):
    title: str
    description: str = None
    rules: str = None
    uuid: str = None
    user_id: Optional[int] = None

class Story(StoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)