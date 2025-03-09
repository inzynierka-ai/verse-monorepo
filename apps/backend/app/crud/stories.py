from sqlalchemy.orm import Session
from app.models.story import Story
from app.schemas import story as story_schema
from fastapi import HTTPException

def get_story(db: Session, story_id: int, user_id: int):
    """Get a story by its ID with optional user filtering"""
    story = db.query(Story).filter(Story.user_id==user_id).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail=f"Story not found")
    return story

def create_story(db: Session, story: story_schema.StoryCreate):
    """Create a new story"""
    db_story = Story(
        title=story.title,
        description=story.description,
        prompt=story.prompt,
        user_id=story.user_id,
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story