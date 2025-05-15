from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException, Depends
from typing import List 
from app.schemas.character_memory import CharacterMemory, CharacterMemoryCreate
from app.db.session import get_db
from app.crud.character_memories import get_memory, save_memory

async def create_character_memories(
    memories_data: List[CharacterMemoryCreate],
    db: Session = Depends(get_db)
):
    """Create multiple memories for characters related to scenes"""
    created_memories = []
    for memory_data in memories_data:
        created_memory = save_memory(
            db=db, 
            character_id=memory_data.character_id, 
            scene_id=memory_data.scene_id, 
            text=memory_data.text
        )
        created_memories.append(created_memory)
    return created_memories
