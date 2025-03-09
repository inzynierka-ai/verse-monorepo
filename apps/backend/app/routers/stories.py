from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas import story as story_schema
from app.schemas import chapter as chapter_schema
from app.db.session import get_db
from app.crud.stories import get_story, create_story as create_story_service
from app.services.users import get_user
from app.schemas.user import User
from app.services.auth import get_current_user

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

@router.post("", response_model=story_schema.Story)
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