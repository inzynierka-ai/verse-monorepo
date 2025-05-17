from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas import character as character_schema
from app.schemas.character_memory import CharacterMemory
from app.schemas.character_memory import CharacterMemoryCreate
from app.db.session import get_db
from app.crud.character_memories import get_memory
from app.crud.character_memories import save_memory
from app.crud.character_memories import get_similar_memories
from app.utils.embedding import get_embedding  # Your wrapper around OpenAI or similar
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter(
    prefix="/characters_memories",
    tags=["character_memories"]
)

@router.get("/{memory_uuid}", response_model=CharacterMemory)
async def get_memory_by_uuid(memory_uuid: str, db: Session = Depends(get_db)):
    """Get a specific memory by UUID"""
    memory = get_memory(db, memory_uuid)
    if not memory:
        raise HTTPException(status_code=404, detail=f"Memory with UUID {memory_uuid} not found")    
    return memory

@router.post("/query/", response_model=List[CharacterMemory])
def get_similar_memories_f(
    character_id: int,
    query: str,
    top_n: int = 3,
    db: Session = Depends(get_db)
):
    """Get similar memories for a character"""
    query_embedding = get_embedding(query)  # should return a list[float]
    if not query_embedding: 
        raise HTTPException(status_code=400, detail="Invalid query embedding")
    
    memories = get_similar_memories(db, character_id, query_embedding, top_n)
    if not memories:
        raise HTTPException(status_code=404, detail="No similar memories found")
    
    # Convert query embedding to numpy array for similarity calculation
    query_embedding_np = np.array(query_embedding).reshape(1, -1)
    
    # Print similarity for each memory
    for memory in memories:
        if hasattr(memory, 'embedding'):
            # Convert memory embedding to numpy array
            memory_embedding_np = np.array(memory.embedding).reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(query_embedding_np, memory_embedding_np)[0][0]
            
            print(f"Memory ID: {memory.uuid}, Similarity: {similarity:.4f}")
    
    return memories

@router.post("/bulk", response_model=List[CharacterMemory])
async def create_character_memories(
    memories_data: List[CharacterMemoryCreate],
    db: Session = Depends(get_db)
):
    """Create multiple memories for characters related to scenes"""
    created_memories = []
    for memory_data in memories_data:
        created_memory = save_memory(
            db=db, 
            character_id=memory_data.character_id, 
            scene_id=memory_data.scene_id, 
            text=memory_data.text
        )
        created_memories.append(created_memory)
    return created_memories




@router.post("/", response_model=CharacterMemory)
async def create_character_memory(
    memory_data: CharacterMemoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new memory for a character related to a scene"""
    return save_memory(
        db=db, 
        character_id=memory_data.character_id, 
        scene_id=memory_data.scene_id, 
        text=memory_data.text
    )