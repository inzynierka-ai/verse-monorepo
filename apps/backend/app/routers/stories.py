import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, cast
from app.schemas import story as story_schema
from app.schemas import scene as scene_schema
from app.db.session import get_db
from app.crud.stories import get_story, create_story as create_story_service
from app.services.users import get_user
from app.schemas.user import User
from app.services.auth import get_current_user
from app.services.scene_service import SceneService
from app.services.game_engine.orchestrators.memory_manager import MemoryManager

router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)
@router.get("/", response_model=List[story_schema.StoryRead])
async def list_stories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all available stories"""
    user = get_user(db, current_user.username)
    stories = user.stories
    return stories

@router.get("/{story_id}", response_model=story_schema.StoryRead)
def get_story_by_id(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific story by ID"""
    story = get_story(db, story_id, current_user.id)
    return story

@router.post("/", response_model=story_schema.StoryRead)
def create_story(
    story: story_schema.StoryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new story"""
    # Create a copy of the story data and inject the user_id
    story_data = story.dict()
    story_data["user_id"] = current_user.id
    
    # Create a new StoryCreate instance with the updated data
    story_with_user = story_schema.StoryCreate(**story_data)
    
    return create_story_service(db, story_with_user)

@router.get("/{story_id}/characters", response_model=List[scene_schema.Character])
def list_characters(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all characters for a specific story"""
    story = get_story(db, story_id, current_user.id)
    characters = story.characters
    return characters


@router.get("/{story_uuid}/scene/latest", response_model=scene_schema.Scene)
def get_latest_scene(
    story_uuid: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest active scene for a story"""
    # Verify user owns the story
    story = get_story(db, story_uuid, current_user.id)
    
    # Get the story ID as an integer
    story_id = cast(int, story.id)
    
    # Instantiate the service and call the method
    scene_service = SceneService()
    latest_scene = scene_service.fetch_latest_active_scene(db, story_id)
    
    # Handle not found cases
    if not latest_scene:
        raise HTTPException(status_code=404, detail="No active scene found for this story")
    
    return latest_scene

@router.patch("/{story_uuid}/scenes/{scene_uuid}/complete", response_model=scene_schema.Scene)
async def complete_scene(  # Make this function async
    story_uuid: uuid.UUID,
    scene_uuid: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a scene as completed"""
    # Verify user owns the story
    story = get_story(db, story_uuid, current_user.id)
    
    # Get the story ID as an integer
    story_id = cast(int, story.id)
    
    memory_manager = MemoryManager(db_session=db)
    # Add await keyword here
    character_memories = await memory_manager.create_memories(db, scene_uuid)

    # Mark the scene as completed
    scene_service = SceneService()
    completed_scene = scene_service.mark_scene_completed(db, scene_uuid, story_id)
    
    # Handle not found cases
    if not completed_scene:
        raise HTTPException(status_code=404, detail="Scene not found or already completed")
    
    return completed_scene