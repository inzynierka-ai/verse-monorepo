import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.models.scene import Scene, SceneSummary
from app.crud import characters as characters_crud

from typing import List, Optional, Dict, Any
import uuid

def get_scene(db: Session, scene_id: int):
    """Get a scene by its ID with all relationships loaded"""
    return db.query(Scene).options(
        joinedload(Scene.location),
        joinedload(Scene.characters),
        joinedload(Scene.messages)
    ).filter(Scene.id == scene_id).first()



def get_scene_by_uuid(db: Session, scene_uuid: str) -> Optional[Scene]:
    """Fetch a scene by its UUID"""
    scene = db.query(Scene).options(
        joinedload(Scene.location),
        joinedload(Scene.characters),
        joinedload(Scene.messages)
    ).filter(
        Scene.uuid == scene_uuid
    ).first()

    return scene

def get_latest_scene_by_story(db: Session, story_id: int) -> Optional[Scene]:
    """Fetch the latest scene for a story"""
    latest_scene = db.query(Scene).options(
        joinedload(Scene.location),
        joinedload(Scene.characters),
        joinedload(Scene.messages)
    ).filter(
        Scene.story_id == story_id
    ).order_by(
        desc(Scene.id)
    ).first()

    return latest_scene

def get_latest_active_scene_by_story(db: Session, story_id: int) -> Optional[Scene]:
    """Fetch the latest active scene for a story"""
    latest_active_scene = db.query(Scene).options(
        joinedload(Scene.location),
        joinedload(Scene.characters),
        joinedload(Scene.messages)
    ).filter(
        Scene.story_id == story_id,
        Scene.status == "active"
    ).order_by(
        desc(Scene.id)
    ).first()

    return latest_active_scene

def get_latest_completed_scene_by_story(db: Session, story_id: int) -> Optional[Scene]:
    """Fetch the latest completed scene for a story"""
    latest_completed_scene = db.query(Scene).options(
        joinedload(Scene.location),
        joinedload(Scene.characters),
        joinedload(Scene.messages)
    ).filter(
        Scene.story_id == story_id,
        Scene.status == "completed"
    ).order_by(
        desc(Scene.id)
    ).first()

    return latest_completed_scene

def mark_scene_as_completed(db: Session, scene_uuid: uuid.UUID, story_id: int) -> Optional[Scene]:
    """Mark a scene as completed and return the updated scene"""
    scene = db.query(Scene).options(
        joinedload(Scene.location),
        joinedload(Scene.characters),
        joinedload(Scene.messages)
    ).filter(
        Scene.uuid == str(scene_uuid),
        Scene.story_id == story_id
    ).first()
    
    if not scene:
        return None
    
    # Set the scene status
    setattr(scene, "status", "completed")
    db.commit()
    db.refresh(scene)
    
    return scene

def get_scene_with_messages(db: Session, scene_id: int) -> Optional[Scene]:
    """Get a scene with its messages for analysis"""
    scene = db.query(Scene).options(
        joinedload(Scene.messages)
    ).filter(
        Scene.id == scene_id
    ).first()
    
    return scene

def update_scene_status(db: Session, scene_id: int, status: str) -> Scene:
    """
    Update the scene status
    
    Args:
        db: Database session
        scene_id: ID of the scene to update
        status: New status value ('generation_not_started', 'generating', 'active', 'completed', 'failed')
        
    Returns:
        The updated scene
    """
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise ValueError(f"Scene with ID {scene_id} not found")
    
    scene.status = status
    db.commit()
    db.refresh(scene)
    
    return scene


def create_or_update_scene_summary(
    db: Session, 
    scene_id: int, 
    summary_data: Dict[str, Any]
) -> SceneSummary:
    """
    Create or update a scene summary
    
    Args:
        db: Database session
        scene_id: ID of the scene to summarize
        summary_data: Dictionary containing summary data
        
    Returns:
        The created or updated SceneSummary object
    """
    # Check if a summary already exists for this scene
    existing_summary = db.query(SceneSummary).filter(
        SceneSummary.scene_id == scene_id
    ).first()
    
    if existing_summary:
        # Update existing summary
        for key, value in summary_data.items():
            setattr(existing_summary, key, value)
        summary = existing_summary
    else:
        # Create new summary
        summary = SceneSummary(
            scene_id=scene_id,
            total_messages=summary_data["total_messages"],
            character_participation=summary_data["character_participation"],
            key_events=summary_data["key_events"],
            sentiment=summary_data["sentiment"],
            relationships=summary_data["relationships"]
        )
        db.add(summary)
    
    db.commit()
    db.refresh(summary)
    
    return summary

def add_characters_to_scene(db: Session, scene_id: int, character_uuids: List[str]):
    """
    Associate characters with a scene using UUIDs instead of database IDs
    
    Args:
        db: Database session
        scene_id: ID of the scene to add characters to
        character_uuids: List of character UUIDs to associate with the scene
        
    Returns:
        The updated scene with character associations
    """
    # Get the scene
    db_scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not db_scene:
        raise ValueError(f"Scene with ID {scene_id} not found")
    
    # Get characters by UUID using the characters_crud module
    for character_uuid in character_uuids:
        character = characters_crud.get_character_by_uuid(db, character_uuid)
        if character:
            # Add to the relationship collection if not already present
            if character not in db_scene.characters:
                db_scene.characters.append(character)
    
    # Commit changes
    db.commit()
    db.refresh(db_scene)
    return db_scene

def create_complete_scene(
    db: Session, 
    story_id: int, 
    location_id: int, 
    description: str,
    character_uuids: Optional[List[str]] = None
) -> Scene:
    """
    Create a complete scene with all required data using character UUIDs instead of IDs
    
    Args:
        db: Database session
        story_id: ID of the story to associate with
        location_id: ID of the location to associate with
        description: Scene description
        character_uuids: Optional list of character UUIDs to associate
        
    Returns:
        The created scene database model
    """
    scene_uuid = str(uuid.uuid4())
    db_scene = Scene(
        uuid=scene_uuid,
        description=description,
        story_id=story_id,
        location_id=location_id,
        status="active"
    )
    
    db.add(db_scene)
    db.flush()
    
    # Store ID before we might lose it in refresh
    scene_id = db_scene.id

    logging.info("character_uuids: " + str(character_uuids))
    
    # Add characters if provided
    if character_uuids:
        # Get fresh copy of scene first
        db_scene = db.query(Scene).filter(Scene.id == scene_id).first()
        if db_scene:
            db_scene = add_characters_to_scene(db, scene_id, character_uuids)
    
    db.commit()
    db.refresh(db_scene)
    
    return db_scene
