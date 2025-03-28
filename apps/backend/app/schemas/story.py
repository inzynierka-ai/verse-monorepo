from pydantic import BaseModel
from typing import Optional

class StoryBase(BaseModel):
    user_id: int
    title: str
    description: str
    rules: Optional[str] = None

class StoryCreate(StoryBase):
    pass

class Story(StoryBase):
    id: int

    class Config:
        from_attributes = True