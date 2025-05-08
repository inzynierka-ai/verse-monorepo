from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas import character as character_schema
from app.db.session import get_db
from app.crud.character_memories import get_memory

router = APIRouter(
    prefix="/characters_memories",
    tags=["character_memories"]
)

@router.get("/{memory_uuid}", response_model=character_schema.Character)
async def get_memory_by_uuid(memory_uuid: str, db: Session = Depends(get_db)):
    """Get a specific memory by UUID"""
    memory = get_memory(db, memory_uuid)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory with UUID {memory_uuid} not found")    
    return memory
