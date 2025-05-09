from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas import character as character_schema
from app.schemas.character_memory import CharacterMemory
from app.db.session import get_db
from app.crud.character_memories import get_memory
from app.crud.character_memories import save_memory

router = APIRouter(
    prefix="/characters_memories",
    tags=["character_memories"]
)

@router.get("/{memory_uuid}", response_model=CharacterMemory)
async def get_memory_by_uuid(memory_uuid: str, db: Session = Depends(get_db)):
    """Get a specific memory by UUID"""
    memory = get_memory(db, memory_uuid)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory with UUID {memory_uuid} not found")    
    return memory

from app.schemas.character_memory import CharacterMemoryCreate

@router.post("/", response_model=CharacterMemory)
async def create_character_memory(
    memory_data: CharacterMemoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new memory for a character related to a scene"""
    return save_memory(
        db=db, 
        character_id=memory_data.character_id, 
        scene_id=memory_data.scene_id, 
        text=memory_data.text
    )