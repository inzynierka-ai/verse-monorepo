from sqlalchemy.orm import Session
from typing import List, Dict
from app.models.world_entity import WorldEntity as WorldEntityModel

def get_entity_names_by_story_id(db: Session, story_id: int) -> List[str]:
    entities = db.query(WorldEntityModel).filter(WorldEntityModel.story_id == story_id).all()
    return [e.name for e in entities]

def get_entity_by_id(db: Session, entity_id: int) -> WorldEntityModel | None:
    """
    Get world entity by ID.
    """
    return db.query(WorldEntityModel).filter(WorldEntityModel.id == entity_id).first()

def get_entities_by_story_id(db: Session, story_id: int) -> List[WorldEntity]:
    """
    Get all world entities by story ID.
    
    Args:
        db: Database session
        story_id: ID of the story to get entities for
        
    Returns:
        List of dictionaries with entity data in format matching the schema
    """
    entities = db.query(WorldEntityModel).filter(WorldEntityModel.story_id == story_id).all()
    
    # Return data in the format expected by the schema
    return [
return [
        WorldEntity(
            id=e.id,
            name=e.name,
            story_id=e.story_id,  # Add this!
            canonical_description=e.canonical_description,  # Use correct field name
            embedding=e.embedding.tolist() if e.embedding is not None else None,
            aliases=e.aliases or [],
            discovered_in_scene=e.discovered_in_scene,
            created_at=e.created_at
        )
        for e in entities
    ]

def get_related_entities(db: Session, name: str, story_id: int, top_k: int = 5) -> List[Dict]:
    """
    Return top-k semantically similar entities by embedding similarity.
    """
    from sqlalchemy.sql import text
    
    # Get semantically similar entities from the same story
    query = text("""
        SELECT name, canonical_description
        FROM world_entities
        WHERE 
            story_id = :story_id
            AND name != :name
        ORDER BY embedding <-> (SELECT embedding FROM world_entities WHERE name = :name AND story_id = :story_id LIMIT 1)
        LIMIT :limit
    """)
    
    result = db.execute(query, {
        "name": name, 
        "story_id": story_id,
        "limit": top_k
    }).fetchall()
    
    return [{"name": r[0], "description": r[1]} for r in result]