from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime
from app.models.world_entity import WorldEntity as WorldEntityModel
from app.schemas.world_entity import WorldEntity, WorldEntityFromLLM
from app.utils.embedding import get_embedding
import logging

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
        WorldEntity(
            id=e.id,
            name=e.name,
            story_id=e.story_id,
            canonical_description=e.canonical_description,
            embedding=e.embedding.tolist() if e.embedding is not None else None,
            aliases=e.aliases or [],
            discovered_in_scene=e.discovered_in_scene,
            created_at=e.created_at
        )
        for e in entities
    ]

def get_related_entities(db: Session, query_embedding: List[float], story_id: int, 
                        top_n: int = 5, similarity_threshold: float = 0.3):
    """
    Get related world entities based on embedding similarity.
    """
    try:
        # For Postgres with pgvector, we can calculate cosine similarity directly
        # 1 - (a <=> b) gives us cosine similarity where higher values = more similar
        stmt = (
            select(WorldEntityModel, (1 - WorldEntityModel.embedding.cosine_distance(query_embedding)).label("similarity"))
            .where(WorldEntityModel.story_id == story_id)
            .where(WorldEntityModel.embedding.is_not(None))
            # Filter by similarity threshold
            .where((1 - WorldEntityModel.embedding.cosine_distance(query_embedding)) >= similarity_threshold)
            # Order by similarity (highest first)
            .order_by((1 - WorldEntityModel.embedding.cosine_distance(query_embedding)).desc())
            .limit(top_n)
        )
        
        results = db.execute(stmt).all()
        
        # Log the results for debugging
        entities_with_scores = []
        for entity, similarity in results:
            logging.info(f"Found related entity: {entity.name} with similarity score: {similarity:.4f}")
            entities_with_scores.append((entity, similarity))
        
        # Return just the entity objects
        return [entity for entity, similarity in entities_with_scores]
    except Exception as e:
        logging.error(f"Error in get_related_entities: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return []
    
def get_related_entities_by_name(db: Session, entity_name: str, story_id: int, 
                              top_n: int = 5, similarity_threshold: float = 0.3):
    """
    Get related world entities based on a name string.
    Generates an embedding from the name and uses that for similarity search.
    """
    try:
        # Generate embedding from the entity name
        query_embedding = get_embedding(entity_name)
        if not query_embedding:
            logging.error(f"Failed to generate embedding for entity name: {entity_name}")
            return []
            
        logging.info(f"Generated embedding for '{entity_name}' with length {len(query_embedding)}")
        
        # Use the existing function with the generated embedding
        return get_related_entities(db, query_embedding, story_id, top_n, similarity_threshold)
        
    except Exception as e:
        logging.error(f"Error in get_related_entities_by_name: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return []

# Add a version that finds entities by name too
def get_entities_by_name(db: Session, query: str, story_id: int, search_descriptions: bool = False):
    """
    Get entities that match the given name query string, including aliases and optionally descriptions.
    
    Args:
        db: Database session
        query: Name string to search for
        story_id: ID of the story to get entities for
        search_descriptions: Whether to also search in entity descriptions
        
    Returns:
        List of entities that match the query
    """
    try:
        from sqlalchemy import or_
        
        # Build query conditions
        conditions = [
            WorldEntityModel.story_id == story_id,
            or_(
                WorldEntityModel.name.ilike(f"%{query}%"),
                WorldEntityModel.aliases.any(lambda alias: alias.ilike(f"%{query}%"))
            )
        ]
        
        # Add description search if requested
        if search_descriptions:
            conditions.append(WorldEntityModel.canonical_description.ilike(f"%{query}%"))
        
        # Execute the query
        entities = db.query(WorldEntityModel).filter(*conditions).all()
            
        log_source = "name, aliases, and descriptions" if search_descriptions else "name and aliases"
        logging.info(f"Search for '{query}' in {log_source} found {len(entities)} entities")
        return entities
        
    except Exception as e:
        logging.error(f"Error searching entities by {log_source}: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return []


def save_entity(db: Session, entity_data: WorldEntityFromLLM, story_id: int, 
               scene_uuid: Optional[str] = None) -> Optional[int]:
    """
    Save a new world entity to the database.
    
    Args:
        db: Database session
        entity_data: WorldEntityFromLLM object containing entity information
        story_id: ID of the story this entity belongs to
        scene_uuid: UUID of the scene where entity was discovered (optional)
        
    Returns:
        ID of the saved entity if successful, None otherwise
    """
    try:
        if not entity_data or not entity_data.name or not entity_data.description:
            logging.warning("Cannot save entity with missing required fields")
            return None

        # Generate embedding for the entity description
        embedding = get_embedding(entity_data.description)
        
        # Explicitly set the created_at timestamp to ensure it's not NULL
        current_time = datetime.utcnow()
        
        # Process aliases
        aliases = []
        if hasattr(entity_data, 'aliases') and entity_data.aliases:
            aliases = entity_data.aliases
            logging.info(f"Entity '{entity_data.name}' has {len(aliases)} aliases: {aliases}")
        else:
            logging.info(f"Entity '{entity_data.name}' has no aliases")
        
        # Create new entity instance
        db_entity = WorldEntityModel(
            name=entity_data.name,
            canonical_description=entity_data.description,
            embedding=embedding,
            discovered_in_scene=scene_uuid,
            story_id=story_id,
            created_at=current_time,
            aliases=aliases
        )

        # Save to database
        db.add(db_entity)
        db.commit()
        db.refresh(db_entity)
        
        logging.info(f"Saved new world entity: {entity_data.name} (ID: {db_entity.id}) at {current_time}")
        return db_entity.id
        
    except Exception as e:
        logging.error(f"Failed to save world entity: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        if db and db.is_active:
            db.rollback()
        return None