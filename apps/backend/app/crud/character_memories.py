from sqlalchemy.orm import Session
from sqlalchemy import select
from app.utils.embedding import get_embedding  # Your wrapper around OpenAI or similar
from fastapi import HTTPException
from app.models.character_memory import CharacterMemory
import uuid


def save_memory(db: Session, character_id: int, scene_id: int, text: str):
    embedding = get_embedding(text)  # should return a list[float]

    memory = CharacterMemory(
        character_id=character_id,
        scene_id=scene_id,
        memory_text=text,
        embedding=embedding,
        uuid=uuid.uuid4()
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


def get_memory(db: Session, memory_uuid: str):
    stmt = select(CharacterMemory).where(CharacterMemory.uuid == memory_uuid)
    memory = db.execute(stmt).scalar_one_or_none()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


def get_similar_memories(db: Session, character_id: int, query_embedding: list[float],
                         top_n: int = 3, similarity_threshold: float = 0.3):
    """
    Get similar memories for a character that exceed a minimum similarity threshold.

    Args:
        db: Database session
        character_id: ID of the character
        query_embedding: Vector embedding of the query
        top_n: Maximum number of memories to return
        similarity_threshold: Minimum similarity score (0-1) for a memory to be included

    Returns:
        List of memories that meet the threshold, ordered by similarity (highest first)
    """
    # For Postgres with pgvector, we can calculate cosine similarity directly
    # 1 - (a <=> b) gives us cosine similarity where higher values = more similar
    stmt = (
        select(CharacterMemory, (1 -
               CharacterMemory.embedding.cosine_distance(query_embedding)).label("similarity"))
        .where(CharacterMemory.character_id == character_id)
        # Filter by similarity threshold
        .where((1 - CharacterMemory.embedding.cosine_distance(query_embedding)) >= similarity_threshold)
        # Order by similarity (highest first)
        .order_by((1 - CharacterMemory.embedding.cosine_distance(query_embedding)).desc())
        .limit(top_n)
    )

    results = db.execute(stmt).all()

    # Return just the memory objects
    return [memory for memory, similarity in results]
