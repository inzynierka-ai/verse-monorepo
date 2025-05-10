from sqlalchemy.orm import Session

def get_all_entity_names(db: Session) -> List[str]:
    return [row.name for row in db.query(WorldEntityModel.name).all()]

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
