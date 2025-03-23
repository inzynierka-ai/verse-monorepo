from pydantic import BaseModel
from typing import Optional

class CharacterBase(BaseModel):
    name: str
    role: str 
    description: str
    details: str 
    relationship_level: int
    story_id: int
    image_dir: Optional[str] = None
    image_prompt: Optional[str] = None 

class CharacterCreate(CharacterBase):
    pass

class Character(CharacterBase):
    id: int

    class Config:
        from_attributes = True