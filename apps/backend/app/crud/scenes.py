import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.models.scene import Scene
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


def get_completed_scenes_by_story(db: Session, story_id: int) -> List[Scene]:
    """Fetch all completed scenes for a story"""
    completed_scenes = db.query(Scene).options(
        joinedload(Scene.location),
        joinedload(Scene.characters),
        joinedload(Scene.messages)
    ).filter(
        Scene.story_id == story_id,
        Scene.status == "completed"
    ).order_by(
        desc(Scene.id)
    ).all()

    return completed_scenes


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


def add_characters_to_scene(db: Session, scene_id: int, characters_data: List[Dict[str, Any]]):
    """
    Associate characters with a scene and update their immediate_goals.

    Args:
        db: Database session
        scene_id: ID of the scene to add characters to
        characters_data: List of dictionaries, each with character 'uuid' and 'immediate_goals'

    Returns:
        The updated scene with character associations
    """
    # Get the scene
    db_scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not db_scene:
        raise ValueError(f"Scene with ID {scene_id} not found")

    # Get characters by UUID using the characters_crud module and update immediate_goals
    for char_data in characters_data:
        character_uuid = char_data.get('uuid')
        immediate_goals = char_data.get('immediate_goals')

        if not character_uuid:
            logging.warning("Character data missing UUID, skipping.")
            continue

        character = characters_crud.get_character_by_uuid(db, character_uuid)
        if character:
            # Update immediate_goals if provided
            if immediate_goals is not None:
                character.immediate_goals = immediate_goals

            # Add to the relationship collection if not already present
            if character not in db_scene.characters:
                db_scene.characters.append(character)
        else:
            logging.warning(
                f"Character with UUID {character_uuid} not found, cannot associate with scene or update goals.")

    # Commit changes
    db.commit()
    db.refresh(db_scene)
    return db_scene


def create_complete_scene(
    db: Session,
    story_id: int,
    location_id: int,
    description: str,
    characters_data: Optional[List[Dict[str, Any]]] = None
) -> Scene:
    """
    Create a new complete scene with characters and a location.

    Args:
        db: Database session
        story_id: ID of the story to associate with
        location_id: ID of the location to associate with
        description: Scene description
        characters_data: Optional list of dictionaries, each with character 'uuid' and 'immediate_goals'

    Returns:
        The created scene model
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
    db.commit()  # Commit to get db_scene.id
    db.refresh(db_scene)

    logging.info(f"Created scene with ID {db_scene.id}")

    # Associate characters with the scene if provided
    if characters_data:
        # The add_characters_to_scene function will handle the association
        # and update immediate_goals for each character.
        # Pass the full characters_data
        add_characters_to_scene(db, db_scene.id, characters_data)

    db.refresh(db_scene)  # Refresh again after characters are added
    return db_scene


def update_scene_summary(db: Session, scene_id: int, summary: str) -> Scene:
    """Update the summary of a scene"""
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise ValueError(f"Scene with ID {scene_id} not found")
    scene.summary = summary
    db.commit()
    db.refresh(scene)
    return scene
