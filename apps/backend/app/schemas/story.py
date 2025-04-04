from pydantic import BaseModel, ConfigDict
from typing import Optional

class StoryBase(BaseModel):
    user_id: int
    title: str
    description: str
    rules: Optional[str] = None
    uuid: str

class StoryCreate(StoryBase):
    pass

class Story(StoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)