from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Optional

from app.models.chapter import Chapter
from app.models.scene import Scene

class SceneService:
    def fetch_latest_scene(self, db: Session, story_id: int) -> Optional[Scene]:
        """Fetches the most recent scene for a given story ID."""
        # Find the latest chapter for the story
        latest_chapter = db.query(Chapter).filter(
            Chapter.story_id == story_id
        ).order_by(
            desc(Chapter.id)  # Assuming higher IDs are newer chapters
        ).first()

        if not latest_chapter:
            return None  # No chapters found for this story

        # Find the latest scene within that chapter
        latest_scene = db.query(Scene).options(
            joinedload(Scene.location),
            joinedload(Scene.characters),
            joinedload(Scene.messages)  # Eager load relationships
        ).filter(
            Scene.chapter_id == latest_chapter.id
        ).order_by(
            desc(Scene.id)  # Assuming higher IDs are newer scenes
        ).first()

        return latest_scene # Returns the scene object or None if no scene found 