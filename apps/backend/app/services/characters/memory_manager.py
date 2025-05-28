import numpy as np
import logging
import sys
import uuid
import traceback
from fastapi import HTTPException
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.services.platform.llm import LLMService, ModelName
from app.utils.json_service import JSONService
from app.models.character import Character
from app.models.scene import Scene
from app.models.character_memory import CharacterMemory as CharacterMemoryModel
from app.utils.embedding import get_embedding
from app.crud.messages import get_messages_by_scene_and_character
from app.schemas.character_memory import CharacterMemoryCreate
from app.crud.character_memories import save_memory, get_similar_memories

class MemoryManager:
    """
    Service for generating character memories from conversation messages.
    """
    def __init__(self, llm_service: Optional[LLMService] = None, db_session: Optional[Session] = None):
        self.llm_service = llm_service or LLMService()
        self.db_session = db_session
        logging.info("MemoryManager initialized")

    async def create_memories(self, db_session: Session, scene_uuid: uuid.UUID) -> List[Any]:
        """
        Creates memories for all characters in a scene based on their conversation messages.
        """
        logging.info(f"Starting memory creation for scene {scene_uuid}")
        
        if not self.db_session:
            logging.error("No database session available, cannot create memories")
            return []
            
        try:
            # Get the scene by UUID
            scene = db_session.query(Scene).filter_by(uuid=str(scene_uuid)).first()
            if not scene:
                print(f"DEBUG: Scene with UUID {scene_uuid} not found")
                return []

            # Get characters associated with this scene through the many-to-many relationship
            characters = scene.characters
            print(f"DEBUG: Found characters: {[c.name for c in characters] if characters else 'None'}")
            if not characters:
                return []
                
            logging.info(f"Found {len(characters)} characters in scene {scene_uuid}")
            
            memories_created = []
            for character in characters:
                try:
                    logging.info(f"Processing character {character.name} with UUID {character.uuid}")
                    
                    memory_chunks = self.create_memory_chunks(scene, character)
                    logging.info(f"Created {len(memory_chunks)} memory chunks for character {character.name}")
                    
                    for memory_chunk in memory_chunks:
                        memory_id = await self.save_character_memory(memory_chunk)
                        if memory_id:
                            memories_created.append(memory_id)
                            logging.info(f"Memory saved with ID: {memory_id}")
                        else:
                            logging.warning(f"Failed to save memory chunk for character {character.name}")
                except Exception as e:
                    logging.error(f"Error processing character {character.name}: {str(e)}")
                    traceback.print_exc()
            
            logging.info(f"Memory creation completed, created {len(memories_created)} memories")
            return memories_created
            
        except Exception as e:
            logging.error(f"Error in create_memories: {str(e)}")
            traceback.print_exc()
            return []

    def create_memory_chunks(self, scene: Scene, character: Character) -> List[Dict[str, Any]]:
        """
        Creates overlapping 3-message chunks of messages for a given scene and character.
        Each chunk is returned as a separate dictionary.
        """
        try:
            logging.info(f"Creating overlapping memory chunks for scene {scene.uuid} and character {character.uuid}")
            
            if not self.db_session:
                logging.error("No database session available, cannot create memory chunks")
                return []
                
            messages = get_messages_by_scene_and_character(self.db_session, scene.uuid, character.uuid)
            if not messages:
                logging.warning(f"No conversation found for scene {scene.uuid} and character {character.uuid}.")    
                return []

            # Need at least 3 messages to create a chunk
            if len(messages) < 3:
                logging.warning(f"Not enough messages ({len(messages)}) to create overlapping chunks")
                # Still create a chunk if there are 1-2 messages
                if messages:
                    chunk_text = "\n".join([str(msg) for msg in messages])
                    return [{
                        "text": chunk_text,
                        "character_id": character.id,
                        "scene_id": scene.id,
                    }]
                return []
            
            # Create overlapping chunks
            chunk_size = 3
            memory_chunks = []
            
            for i in range(len(messages) - chunk_size + 1):
                chunk = messages[i:i + chunk_size]
                chunk_text = "\n".join([str(msg) for msg in chunk])
                
                memory_chunks.append({
                    "text": chunk_text,
                    "character_id": character.id,
                    "scene_id": scene.id,
                })
            
            logging.info(f"Created {len(memory_chunks)} overlapping memory chunks from {len(messages)} messages")
            return memory_chunks
        
        except Exception as e:
            logging.error(f"Error creating memory chunks: {str(e)}")
            traceback.print_exc()
            return []

    async def save_character_memory(self, memory_data: Dict[str, str]):
        """Create a new memory for a character related to a scene"""
        try:
            if not memory_data or not memory_data.get("text"):
                logging.warning("Cannot save empty memory data")
                return None
                
            if not self.db_session:
                logging.error("No database session available, cannot save memory")
                return None
                
            memory_create = CharacterMemoryCreate(
                character_id=memory_data["character_id"], 
                scene_id=memory_data["scene_id"], 
                text=memory_data["text"]
            )
            
            memory = save_memory(
                db=self.db_session,
                character_id=memory_create.character_id, 
                scene_id=memory_create.scene_id, 
                text=memory_create.text
            )
            
            if memory:
                # Return just the ID or UUID instead of the entire object
                memory_id = memory.id if hasattr(memory, 'id') else memory.uuid
                logging.info(f"Successfully saved memory with ID {memory_id}")
            else:
                logging.warning("Failed to save memory, no object returned")
                memory_id = None
                
            return memory_id
        except Exception as e:
            logging.error(f"Error saving character memory: {str(e)}")
            traceback.print_exc()
            return None

    
    async def find_similar_memories(self, character_id: int, query: str, top_n: int = 3, 
                                similarity_threshold: float = 0.2) -> List[CharacterMemoryModel]:
        """
        Get similar memories for a character that meet minimum similarity threshold.
        """
        try:
            logging.info(f"Finding similar memories for character {character_id}, query: '{query[:50]}...'")
            
            if not self.db_session:
                logging.error("No database session available, cannot find similar memories")
                return []
                
            if not query or not character_id:
                logging.warning("Missing required parameters (character_id or query)")
                return []
                
            query_embedding = get_embedding(query)  
            if not query_embedding: 
                logging.error("Could not generate embedding for query")
                raise HTTPException(status_code=400, detail="Invalid query embedding")
            
            logging.info(f"Generated embedding of length {len(query_embedding)}")
            
            # Get memories that already meet the threshold from the database
            memories = get_similar_memories(
                self.db_session, 
                character_id, 
                query_embedding, 
                top_n,
                similarity_threshold
            )
            
            if not memories:
                logging.info(f"No similar memories found for character {character_id} above threshold {similarity_threshold}")
                return []
            
            logging.info(f"Found {len(memories)} similar memories with similarity >= {similarity_threshold}")
            
            # For debugging/logging purposes, calculate and log similarity for each memory
            query_embedding_np = np.array(query_embedding).reshape(1, -1)
            for memory in memories:
                if hasattr(memory, 'embedding'):
                    memory_embedding_np = np.array(memory.embedding).reshape(1, -1)
                    similarity = cosine_similarity(query_embedding_np, memory_embedding_np)[0][0]
                    logging.info(f"Memory ID: {memory.uuid}, Similarity: {similarity:.4f}, Text: '{memory.memory_text[:50]}...'")
            
            return memories
            
        except Exception as e:
            logging.error(f"Error finding similar memories: {str(e)}")
            traceback.print_exc()
            return []