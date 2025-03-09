from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas import chapter as chapter_schema
from app.schemas import scene as scene_schema
from app.schemas import character as character_schema
from app.schemas import location as location_schema
from app.db.session import get_db
from app.crud.chapters import get_chapter, create_chapter as create_chapter_service
from app.services.auth import ResourcePermission, get_current_user
from app.schemas.user import User

# Create permission checker
chapter_permission = ResourcePermission("chapter")


router = APIRouter(prefix="/chapters",tags=["chapters"])

@router.get("/{chapter_id}", response_model=chapter_schema.Chapter)
def get_chapter_by_id(chapter = Depends(chapter_permission), current_user: User = Depends(get_current_user)):
    """Get a specific chapter that belongs to the current user"""
    return chapter

@router.get("/{chapter_id}/scenes", response_model=List[scene_schema.Scene])
def list_chapter_scenes(chapter = Depends(chapter_permission), current_user: User = Depends(get_current_user)):
    """Get all scenes for a specific chapter that belongs to the current user"""
    return chapter.scenes

@router.get("/{chapter_id}/characters", response_model=List[character_schema.Character])
def list_chapter_characters(chapter = Depends(chapter_permission), current_user: User = Depends(get_current_user)):
    """Get all characters for a specific chapter that belongs to the current user"""
    return chapter.characters

@router.get("/{chapter_id}/locations", response_model=List[location_schema.Location])
def list_chapter_locations(chapter = Depends(chapter_permission), current_user: User = Depends(get_current_user)):
    """Get all locations for a specific chapter that belongs to the current user"""
    return chapter.locations

@router.post("/", response_model=chapter_schema.Chapter)
def create_chapter(
    chapter: chapter_schema.ChapterCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chapter"""
    # Verify user owns the story
    story_permission = ResourcePermission("story")
    story = Depends(story_permission)(chapter.story_id, db, current_user)
    
    return create_chapter_service(db, chapter)