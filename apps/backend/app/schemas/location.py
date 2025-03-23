from pydantic import BaseModel
from typing import Optional

class LocationBase(BaseModel):
    name: str
    description: str
    details: str 
    story_id: int
    image_prompt: Optional[str] = None 

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int

    class Config:
        from_attributes = True