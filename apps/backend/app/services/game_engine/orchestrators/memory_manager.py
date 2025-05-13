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
                            similarity_threshold: float = 0.75) -> List[str]:
        """
        Retrieves relevant memories for a character based on semantic similarity to the last message.
        
        Args:
            character_id: ID of the character whose memories to retrieve
            current_scene_id: ID of the current scene (to exclude memories from this scene)
            last_message_embedding: Vector embedding of the last message/context
            max_memories: Maximum number of memories to return (default: 5)
            similarity_threshold: Minimum similarity score to consider a memory relevant (default: 0.75)
            
        Returns:
            List of relevant memory texts as strings
        """
        if not self.db_session:
            logging.error("No database session available, cannot retrieve relevant memories")
            return []
            
        try:
            
            # Convert Python list to a native pgvector Vector for proper comparison
            embedding_vector = Vector(last_message_embedding)
            
            # Define the query using raw SQL for the vector operations
            # The <-> operator returns negative cosine similarity, so we negate it to get positive similarity
            query = text("""
                WITH similarity_results AS (
                    SELECT 
                        cm.id,
                        cm.memory_text,
                        cm.scene_id, 
                        cm.uuid,
                        1 - (cm.embedding <-> :embedding) AS similarity
                    FROM 
                        character_memories cm
                    WHERE 
                        cm.character_id = :character_id
                        AND cm.scene_id != :current_scene_id
                        AND (1 - (cm.embedding <-> :embedding)) > :threshold
                    ORDER BY 
                        similarity DESC
                    LIMIT :limit
                )
                SELECT 
                    sr.id,
                    sr.memory_text,
                    sr.scene_id,
                    s.name AS scene_name,
                    sr.uuid,
                    sr.similarity
                FROM 
                    similarity_results sr
                JOIN 
                    scenes s ON sr.scene_id = s.id
            """)
            
            # Execute the query with parameters
            result = self.db_session.execute(
                query,
                {
                    "embedding": embedding_vector,
                    "character_id": character_id,
                    "current_scene_id": current_scene_id,
                    "threshold": similarity_threshold,
                    "limit": max_memories
                }
            ).fetchall()
            
            # Format the results
            memories = [
                {
                    "id": row[0],
                    "memory_text": row[1],
                    "scene_id": row[2],
                    "scene_name": row[3],
                    "uuid": row[4],
                    "similarity": float(row[5])  # Convert Decimal to float
                }
                for row in result
            ]
            
            logging.info(f"Retrieved {len(memories)} relevant memories for character {character_id}")
            memory_texts = [memory["memory_text"] for memory in memories]
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