import uuid
from sqlalchemy.orm import Session, contains_eager
from app.models.story import Story
from app.models.character import Character
from app.schemas import story as story_schema
from fastapi import HTTPException

def get_story(db: Session, story_uuid: uuid.UUID, user_id: int):
    """Get a story by its UUID with optional user filtering"""
    story = db.query(Story).filter(Story.user_id==user_id).filter(Story.uuid == str(story_uuid)).first()
    if not story:
        raise HTTPException(status_code=404, detail=f"Story not found")
    return story

def get_user_stories(db: Session, user_id: int):
    """Get all stories for a user, with the player character pre-loaded if available."""
    stories = (
        db.query(Story)
        .outerjoin(Character, (Story.id == Character.story_id) & (Character.role == "player"))
        .options(contains_eager(Story.characters))
        .filter(Story.user_id == user_id)
        .all()
    )
    return stories

def get_story_by_uuid(db: Session, story_uuid: uuid.UUID, user_id: int) -> Story:
    """Get a story by its UUID, ensuring it belongs to the user."""
    story = db.query(Story).filter(Story.user_id == user_id, Story.uuid == str(story_uuid)).first()
    if not story:
        # Use a more specific error message or raise PermissionError if preferred
        raise HTTPException(status_code=404, detail="Story not found or access denied")
    return story

def create_story(db: Session, story: story_schema.StoryCreate):
    """Create a new story"""
    db_story = Story(
        title=story.title,
        description=story.description,
        user_id=story.user_id,
        rules=story.rules,
        uuid=story.uuid 
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story