from pydantic import BaseModel
from typing import Optional, List

class LocationBase(BaseModel):
    name: str
    description: str
    story_id: int
    image_prompt: Optional[str] = None
    rules: Optional[str] = None
    colors: Optional[str] = None
    image_dir: Optional[str] = None
    uuid: str

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int

    class Config:
        from_attributes = True