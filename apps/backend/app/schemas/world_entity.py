from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class WorldEntityBase(BaseModel):
    id: int
    story_id: int
    name: str  
    canonical_description: str
    embedding: Optional[List[float]] = None
    aliases: List[str] = []
    discovered_in_scene: Optional[UUID] = None
    created_at: Optional[datetime] = None

class WorldEntity(WorldEntityBase):
    class Config:
        orm_mode = True
        from_attributes = True

class WorldEntityFromLLM(BaseModel):
    name: str
    description: str

class WorldEntityCreate(BaseModel):
    story_id: int
    name: str  
    canonical_description: str
    
    class Config:
        orm_mode = True
        from_attributes = True