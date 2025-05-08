from pydantic import BaseModel, ConfigDict
from typing import Optional

class CharacterBase(BaseModel):
    name: str
    role: str 
    description: str
    story_id: int
    personality_traits: Optional[str] = None
    backstory: Optional[str] = None
    goals: Optional[str] = None
    speaking_style: Optional[str] = None
    relationships: Optional[str] = None
    image_dir: Optional[str] = None
    image_prompt: Optional[str] = None
    relationship_level: Optional[int] = None
    uuid: str

class CharacterCreate(CharacterBase):
    pass

class Character(CharacterBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class PlayerCharacterRead(BaseModel):
    name: str
    image_dir: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)