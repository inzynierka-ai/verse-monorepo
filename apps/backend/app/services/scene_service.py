from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Optional
from app.models.scene import Scene


class SceneService:
    def fetch_latest_scene(self, db: Session, story_id: int) -> Optional[Scene]:
        """Fetch the latest scene for a story"""
        latest_scene = db.query(Scene).options(
            joinedload(Scene.location),
            joinedload(Scene.characters),
            joinedload(Scene.messages)  # Eager load relationships
        ).filter(
            Scene.story_id == story_id
        ).order_by(
            desc(Scene.id)  # Assuming higher IDs are newer scenes
        ).first()

        if not latest_scene:
            return None  # No scenes found for this story
        return latest_scene # Returns the scene object or None if no scene found 