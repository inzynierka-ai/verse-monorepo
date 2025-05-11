from sqlalchemy.orm import Session
from typing import List, Dict
from app.models.world_entity import WorldEntity as WorldEntityModel

def get_all_entity_names(db: Session) -> List[str]:
    return [row.name for row in db.query(WorldEntityModel.name).all()]

def get_entity_by_id(db: Session, entity_id: int) -> WorldEntityModel | None:
    """
    Get world entity by ID.
    """
    return db.query(WorldEntityModel).filter(WorldEntityModel.id == entity_id).first()

def get_entities_by_story_id(db: Session, story_id: int) -> List[Dict]:
    """
    Get all world entities by story ID.
    """
    entities = db.query(WorldEntityModel).filter(WorldEntityModel.story_id == story_id).all()
    return [{"id": e.id, "name": e.name, "description": e.canonical_description} for e in entities]

def get_related_entities(db: Session, name: str, top_k: int = 5) -> List[Dict]:
    """
    Return top-k semantically similar entities by embedding similarity.
    """
    from sqlalchemy.sql import text
    query = text("""
        SELECT name, canonical_description
        FROM world_entities
        ORDER BY embedding <-> (SELECT embedding FROM world_entities WHERE name = :name LIMIT 1)
        LIMIT :limit
    """)
    result = db.execute(query, {"name": name, "limit": top_k}).fetchall()
    return [{"name": r[0], "description": r[1]} for r in result]
