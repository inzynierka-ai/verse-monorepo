from models.character_memory import CharacterMemory
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import select
from apps.backend.app.utils.embedding import get_embedding  # Your wrapper around OpenAI or similar

def save_memory(db: Session, character_id: int, scene_id: int, text: str):
    embedding = get_embedding(text)  # should return a list[float]

    memory = CharacterMemory(
        character_id=character_id,
        scene_id=scene_id,
        memory_text=text,
        embedding=embedding
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


def get_similar_memories(db: Session, character_id: int, query_embedding: list[float], top_n: int = 3):
    stmt = (
        select(CharacterMemory)
        .where(CharacterMemory.character_id == character_id)
        .order_by(CharacterMemory.embedding.l2_distance(query_embedding))
        .limit(top_n)
    )
    return db.execute(stmt).scalars().all()