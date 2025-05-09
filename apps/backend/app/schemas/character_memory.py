from pydantic import BaseModel

class CharacterMemoryBase(BaseModel):
    id : int
    character_id: int
    scene_id: int
    memory_text: str
    embedding: list[float]
    uuid: str

class CharacterMemory(CharacterMemoryBase):
    pass

class CharacterMemoryCreate(BaseModel):
    character_id: int
    scene_id: int
    text: str
    
    class Config:
        orm_mode = True