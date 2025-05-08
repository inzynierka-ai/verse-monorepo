from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas import character as character_schema
from app.schemas import character_memory as character_memory_schema
from app.db.session import get_db
from app.crud.characters import get_character, get_characters, create_character as create_character_service

router = APIRouter(
    prefix="/characters",
    tags=["characters"]
)
#get all characters
@router.get("/", response_model=List[character_schema.Character])
async def list_characters(db: Session = Depends(get_db)):
    """Get all available characters"""
    return get_characters(db)

# get character by id
@router.get("/{character_id}", response_model=character_schema.Character)
async def get_character_by_id(character_id: int, db: Session = Depends(get_db)):
    """Get a specific character by ID"""
    character = get_character(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail=f"Character with ID {character_id} not found")
    return character 

@router.get("/{character_id}/memories", response_model=List[character_memory_schema.CharacterMemory])
async def get_character_memories(character_id: int, db: Session = Depends(get_db)):
    """Get memories of a specific character by ID"""
    character = get_character(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail=f"Character with ID {character_id} not found")
    return character.memories    

@router.post("", response_model=character_schema.Character)
async def create_character(character: character_schema.CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character"""
    return create_character_service(db, character)
