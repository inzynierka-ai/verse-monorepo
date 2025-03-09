from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import *
from app.schemas import chapter as chapter_schema

def get_chapter(db: Session, chapter_id: int) -> Chapter:
    """Get chapter by ID"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chapter not found")
    return chapter

def create_chapter(db: Session, chapter: chapter_schema.ChapterCreate) -> Chapter:
    """Create a new chapter"""
    db_chapter = Chapter(
        story_id=chapter.story_id,
        title=chapter.title,
        description=chapter.description,
        prompt=chapter.prompt
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter