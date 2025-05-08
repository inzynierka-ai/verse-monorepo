from pydantic import BaseModel

class CharacterMemoryBase(BaseModel):
    id : int
    character_id: int
    scene_id: int
    memory_text: str
    embedding: list[float]  # or Vector, depending on your use case
    uuid: str

class CharacterMemory(CharacterMemoryBase):
    pass