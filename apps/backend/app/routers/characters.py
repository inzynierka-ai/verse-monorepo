from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.schemas import character as character_schema
from app.schemas import character_memory as character_memory_schema
from app.schemas.conversation import ConversationTopicsResponse
from app.db.session import get_db
from app.crud.characters import get_character, get_characters, create_character as create_character_service, get_character_by_uuid
from app.crud.scenes import get_scene_by_uuid
from app.services.scenes.conversation_service import ConversationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/characters",
    tags=["characters"]
)
# get all characters


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
        raise HTTPException(
            status_code=404, detail=f"Character with ID {character_id} not found")
    return character


@router.get("/{character_id}/memories", response_model=List[character_memory_schema.CharacterMemory])
async def get_character_memories(character_id: int, db: Session = Depends(get_db)):
    """Get memories of a specific character by ID"""
    character = get_character(db, character_id)
    if not character:
        raise HTTPException(
            status_code=404, detail=f"Character with ID {character_id} not found")
    return character.memories


@router.post("", response_model=character_schema.Character)
async def create_character(character: character_schema.CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character"""
    return create_character_service(db, character)


@router.post("/{character_uuid}/conversation-topics/{scene_uuid}", response_model=ConversationTopicsResponse)
async def get_conversation_topics(
    character_uuid: str,
    scene_uuid: str,
    db: Session = Depends(get_db),
    messages: Optional[List[Dict[str, Any]]] = Body(None)
):
    """Get suggested conversation topics for a character in a specific scene"""
    character = get_character_by_uuid(db, character_uuid)
    if not character:
        raise HTTPException(
            status_code=404, detail=f"Character with UUID {character_uuid} not found")

    scene = get_scene_by_uuid(db, scene_uuid)
    if not scene:
        raise HTTPException(
            status_code=404, detail=f"Scene with UUID {scene_uuid} not found")

    try:
        conversation_service = ConversationService()
        return await conversation_service.generate_conversation_topics(db, character, scene, messages)

    except Exception as e:
        logger.error(f"Error generating conversation topics: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to generate conversation topics")
