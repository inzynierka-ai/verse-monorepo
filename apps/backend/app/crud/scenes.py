from sqlalchemy.orm import Session, joinedload
from app.models.scene import Scene
from app.schemas import scene as scene_schema

def get_scene(db: Session, scene_id: int):
    """Get a scene by its ID with all relationships loaded"""
    return db.query(Scene).options(
        joinedload(Scene.location),
        joinedload(Scene.characters),
        joinedload(Scene.messages)
    ).filter(Scene.id == scene_id).first()

def create_scene(db: Session, scene: scene_schema.SceneCreate):
    """Create a new scene"""
    db_scene = Scene(
        prompt=scene.prompt, 
        location_id=scene.location_id, 
        story_id=scene.story_id)
    
    db.add(db_scene)
    db.commit()
    db.refresh(db_scene)
    return db_scene