from pydantic import BaseModel
from typing import Optional

class CharacterBase(BaseModel):
    name: str
    role: str 
    description: str
    story_id: int
    personalityTraits: Optional[str] = None
    backstory: Optional[str] = None
    goals: Optional[str] = None
    speaking_style: Optional[str] = None
    relationships: Optional[str] = None
    image_dir: Optional[str] = None
    image_prompt: Optional[str] = None
    relationship_level: Optional[int] = None

class CharacterCreate(CharacterBase):
    pass

class Character(CharacterBase):
    id: int

    class Config:
        from_attributes = True