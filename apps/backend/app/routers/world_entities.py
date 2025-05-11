from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas import character as character_schema
from app.schemas.world_entity import WorldEntity
from app.crud.world_entities import get_entities_by_story_id, get_entity_by_id
from app.crud.scenes import get_scene_by_uuid
from app.services.world_entity_service import WorldEntityService
from app.db.session import get_db


router = APIRouter(
    prefix="/world_entities",
    tags=["world_entities"],
)

@router.get("/{story_id}", response_model=List[WorldEntity])
async def list_all_world_entites_by_story_id(
    db: Session = Depends(get_db),
    story_id: int = None,
):
    """Get all wolrd entities"""
    if not story_id:
        raise HTTPException(status_code=400, detail="story_id is required")
    entities = get_entities_by_story_id(db, story_id)
    return entities

@router.get("/{world_entity_id}", response_model=WorldEntity)
async def get_world_entity_by_id(
    db: Session = Depends(get_db),
    world_entity_id: int = None,
):
    """Get world entity by ID"""
    if not world_entity_id:
        raise HTTPException(status_code=400, detail="world_entity_id is required")
    entity = get_entity_by_id(db, world_entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="World entity not found")
    return entity

@router.post("/", response_model=List[WorldEntity])
async def create_entities(scene_uuid: str, db: Session = Depends(get_db)):
    """Create world entities from a scene"""
    # Get the scene to find its story_id
    scene = get_scene_by_uuid(db, scene_uuid)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
        
    # Create the service with all necessary context
    world_entity_service = WorldEntityService(db_session=db, story_id=scene.story_id)
    
    # Process the scene - now we only pass scene_uuid as expected
    entity_ids = await world_entity_service.process_new_scene_entities(scene_uuid=scene_uuid)
    
    if not entity_ids:
        return []
        
    # Return the created entities
    return [get_entity_by_id(db, entity_id) for entity_id in entity_ids]