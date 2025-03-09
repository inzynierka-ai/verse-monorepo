from pydantic import BaseModel

class CharacterBase(BaseModel):
    name: str
    avatar: str
    description: str
    relationship_level: int
    prompt: str
    story_id: int

class CharacterCreate(CharacterBase):
    pass

class Character(CharacterBase):
    id: int

    class Config:
        from_attributes = True
