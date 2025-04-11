from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List
from app.schemas import story as story_schema
from app.schemas import chapter as chapter_schema
from app.schemas import scene as scene_schema
from app.db.session import get_db
from app.crud.stories import get_story, create_story as create_story_service
from app.services.users import get_user
from app.schemas.user import User
from app.services.auth import get_current_user
from app.models.chapter import Chapter
from app.models.scene import Scene

router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)
@router.get("/", response_model=List[story_schema.Story])
async def list_stories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all available stories"""
    user = get_user(db, current_user.username)
    stories = user.stories
    return stories

@router.get("/{story_id}", response_model=story_schema.Story)
def get_story_by_id(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific story by ID"""
    story = get_story(db, story_id, current_user.id)
    return story

@router.get("/{story_id}/chapters", response_model=List[chapter_schema.Chapter])
def list_chapters(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all chapters for a specific story"""
    story = get_story(db, story_id, current_user.id)
    chapters = story.chapters
    return chapters

@router.post("/", response_model=story_schema.Story)
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

@router.get("/{story_id}/latest-scene", response_model=scene_schema.SceneDetail)
def get_latest_scene(
    story_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest scene for a story"""
    # Verify user owns the story
    get_story(db, story_id, current_user.id)
    
    # Explicitly query for the latest chapter
    latest_chapter = db.query(Chapter).filter(
        Chapter.story_id == story_id
    ).order_by(
        desc(Chapter.id)  # Assuming higher IDs are newer chapters
    ).first()
    
    if not latest_chapter:
        raise HTTPException(status_code=404, detail="No chapters found for this story")
    
    # Query for the latest scene from the latest chapter
    latest_scene = db.query(Scene).options(
        joinedload(Scene.location),
        joinedload(Scene.characters),
        joinedload(Scene.messages)
    ).filter(
        Scene.chapter_id == latest_chapter.id
    ).order_by(
        desc(Scene.id)  # Assuming higher IDs are newer scenes
    ).first()
    
    if not latest_scene:
        raise HTTPException(status_code=404, detail="No scenes found for the latest chapter")
    
    return latest_scene