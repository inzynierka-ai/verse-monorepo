import uuid
import logging
import sys
import traceback
from typing import Optional, Dict, Any, List
from app.services.game_engine.tools.memory_generator import MemoryGenerator
from app.models.character import Character
from app.models.scene import Scene
from app.db.session import Session
from pgvector.sqlalchemy import Vector
from sqlalchemy import text

class MemoryManager:

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initializes the MemoryManager with a database session and a memory generator.
        """
        self.db_session = db_session
        self.memory_generator = MemoryGenerator(db_session=self.db_session)

    async def get_relevant_memories(self, character_id: int, current_scene_id: int, 
                            last_message_embedding: list[float], 
                            max_memories: int = 5, 
                            similarity_threshold: float = 0.1) -> List[str]:
        """
        Retrieves relevant memories for a character based on semantic similarity to the last message.
        
        Args:
            character_id: ID of the character whose memories to retrieve
            current_scene_id: ID of the current scene (to exclude memories from this scene)
            last_message_embedding: Vector embedding of the last message/context
            max_memories: Maximum number of memories to return (default: 5)
            similarity_threshold: Minimum similarity score to consider a memory relevant (default: 0.1)
            
        Returns:
            List of relevant memory texts as strings
        """
        if not self.db_session:
            logging.error("No database session available, cannot retrieve relevant memories")
            return []
            
        try:
            # Convert Python list to a native pgvector Vector for proper comparison
            embedding_vector = str(last_message_embedding)
            
            logging.info(f"Searching for memories for character_id={character_id}, current_scene_id={current_scene_id}")
            
            # First, let's check how many memories this character has in total
            count_query = text("""
                SELECT COUNT(*) FROM character_memories 
                WHERE character_id = :character_id
            """)
            
            total_count = self.db_session.execute(
                count_query,
                {"character_id": character_id}
            ).scalar()
            
            logging.info(f"Total memories for character {character_id}: {total_count}")
            
            # Modified query to get all memories with their similarity scores
            # Removed the similarity threshold filter to see all memories
            query = text("""
                SELECT 
                    cm.id,
                    cm.memory_text,
                    cm.scene_id, 
                    cm.uuid,
                    1 - (cm.embedding <-> :embedding) AS similarity
                FROM 
                    character_memories cm
                JOIN 
                    scenes s ON cm.scene_id = s.id
                WHERE 
                    cm.character_id = :character_id
                    AND cm.scene_id != :current_scene_id
                ORDER BY 
                    similarity DESC
            """)
            
            # Execute the query with parameters
            result = self.db_session.execute(
                query,
                {
                    "embedding": embedding_vector,
                    "character_id": character_id,
                    "current_scene_id": current_scene_id
                }
            ).fetchall()
            
            # Format the results and log each memory with its similarity
            all_memories = []
            for row in result:
                memory = {
                    "id": row[0],
                    "memory_text": row[1],
                    "scene_id": row[2],
                    "uuid": row[3],
                    "similarity": float(row[4])  # Convert Decimal to float
                }
                all_memories.append(memory)
                logging.info(f"Memory: {memory['id']}, Text: '{memory['memory_text'][:50]}...', Similarity: {memory['similarity']:.4f}")
            
            logging.info(f"Retrieved {len(all_memories)} total memories before threshold filtering")
            
            # Now filter by threshold for the actual return value
            filtered_memories = [m for m in all_memories if m["similarity"] > similarity_threshold]
            logging.info(f"After filtering (threshold={similarity_threshold}): {len(filtered_memories)} memories qualify")
            
            # Return the top memories up to max_memories
            top_memories = filtered_memories[:max_memories]
            memory_texts = [memory["memory_text"] for memory in top_memories]
            
            return memory_texts
            
        except Exception as e:
            logging.error(f"Error retrieving relevant memories: {str(e)}")
            traceback.print_exc()
            return []
                
        
    async def create_memories(self, db_session: Session, scene_uuid: uuid.UUID):
        """
        Creates memories for all characters in the current scene.
        """
        print(f"DEBUG: Starting memory creation for scene {scene_uuid}")
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

            memories_created = []
            for character in characters:
                try:
                    print(f"DEBUG: Processing character {character.name} with UUID {character.uuid}")
                    character_uuid = character.uuid
                    # Convert UUID to string for the extract_memories method
                    scene_uuid_str = str(scene_uuid)
                    
                    print(f"DEBUG: About to call extract_memories for {character.name}")
                    sys.stdout.flush()  # Force output to be displayed
                    
                    memories = await self.memory_generator.extract_memories(scene_uuid_str, character_uuid)
                    
                    print(f"DEBUG: Extracted memories for character {character.name}: {memories}")
                    sys.stdout.flush()  # Force output to be displayed
                    
                    for memory in memories:
                        print(f"DEBUG: Saving memory: {memory}")
                        memory_id = await self.memory_generator.save_memory_to_db(memory, scene.id, character.id)
                        if memory_id:
                            memories_created.append(memory_id)
                            print(f"DEBUG: Memory saved with ID: {memory_id}")
                        else:
                            print(f"DEBUG: Failed to save memory: {memory}")
                except Exception as e:
                    print(f"DEBUG: Error processing character {character.name}: {str(e)}")
                    traceback.print_exc()
                    
            print(f"DEBUG: Memory creation completed, created {len(memories_created)} memories")
            return memories_created
            
        except Exception as e:
            print(f"DEBUG: Error in create_memories: {str(e)}")
            traceback.print_exc()
            return []