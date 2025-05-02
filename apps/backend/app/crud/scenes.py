from sqlalchemy.orm import Session, joinedload
from app.models.scene import Scene
from app.models.character import Character

from typing import List

def get_scene(db: Session, scene_id: int):
    """Get a scene by its ID with all relationships loaded"""
    return db.query(Scene).options(
        joinedload(Scene.location),
        joinedload(Scene.characters),
        joinedload(Scene.messages)
    ).filter(Scene.id == scene_id).first()


def add_characters_to_scene(db: Session, scene_id: int, character_ids: List[int]):
    """
    Associate characters with a scene in the scene_character_association table
    
    Args:
        db: Database session
        scene_id: ID of the scene to add characters to
        character_ids: List of character IDs to associate with the scene
        
    Returns:
        The updated scene with character associations
    """
    # Get the scene
    db_scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not db_scene:
        raise ValueError(f"Scene with ID {scene_id} not found")
    
    # Get characters by ID
    for character_id in character_ids:
        character = db.query(Character).filter(Character.id == character_id).first()
        if character:
            # Add to the relationship collection if not already present
            if character not in db_scene.characters:
                db_scene.characters.append(character)
    
    # Commit changes
    db.commit()
    db.refresh(db_scene)
    return db_scene