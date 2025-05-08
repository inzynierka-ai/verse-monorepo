from sqlalchemy.orm import Session
from typing import Optional, cast, Dict, List, Any
import uuid
from app.models.scene import Scene
from app.models.message import Message
from app.crud import scenes


class SceneService:
    def fetch_latest_scene(self, db: Session, story_id: int) -> Optional[Scene]:
        """Fetch the latest scene for a story"""
        return scenes.get_latest_scene_by_story(db, story_id)
    
    def fetch_latest_active_scene(self, db: Session, story_id: int) -> Optional[Scene]:
        """Fetch the latest active scene for a story"""
        return scenes.get_latest_active_scene_by_story(db, story_id)
    
    def fetch_latest_completed_scene(self, db: Session, story_id: int) -> Optional[Scene]:
        """Fetch the latest completed scene for a story"""
        return scenes.get_latest_completed_scene_by_story(db, story_id)
    
    def mark_scene_completed(self, db: Session, scene_uuid: uuid.UUID, story_id: int) -> Optional[Scene]:
        """Mark a scene as completed and return the updated scene"""
        scene = scenes.mark_scene_as_completed(db, scene_uuid, story_id)
        
        if not scene:
            return None
        
        # Process the completed scene
        scene_id = cast(int, scene.id)
        self.process_completed_scene(db, scene_id)
        
        return scene
    
    def process_completed_scene(self, db: Session, scene_id: int) -> None:
        """Process a completed scene to analyze interactions and prepare for next scene generation"""
        scene = scenes.get_scene_with_messages(db, scene_id)
        
        if scene is None:
            return
            
        if getattr(scene, "status") != "completed":
            return
        
        # 1. Fetch all messages for the completed scene
        messages = scene.messages
        
        if not messages:
            return
        
        # 2. Implement summarization logic
        summary_data = self._summarize_scene_messages(messages)
        
        # 3. Store summary data using the CRUD module
        scenes.create_or_update_scene_summary(db, scene_id, summary_data)
        
        # Future enhancement: Update character relationships based on interactions
    
    def _summarize_scene_messages(self, messages: List[Message]) -> Dict[str, Any]:
        """
        Analyze messages from a scene and generate a summary
        
        This is a placeholder implementation. In the future, this could:
        - Extract key events and decisions from the scene
        - Identify important character interactions
        - Analyze sentiment and relationship changes
        - Prepare context for the next scene generation
        
        Args:
            messages: List of Message objects from the scene
            
        Returns:
            Dict containing summary information
        """
        # Simple placeholder implementation
        character_message_counts: Dict[str, int] = {}
        total_messages = len(messages)
        
        for message in messages:
            # Convert to string to avoid SQLAlchemy Column type issues
            character_id = str(message.character_id)
            if character_id in character_message_counts:
                character_message_counts[character_id] += 1
            else:
                character_message_counts[character_id] = 1
        
        # Basic summary structure - this would be much more sophisticated in a real implementation
        summary: Dict[str, Any] = {
            "total_messages": total_messages,
            "character_participation": character_message_counts,
            "key_events": [],  # Placeholder for future NLP analysis
            "sentiment": {},   # Placeholder for future sentiment analysis
            "relationships": {} # Placeholder for future relationship tracking
        }
        
        return summary 