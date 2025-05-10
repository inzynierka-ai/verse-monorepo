import uuid
import sys
import traceback
from typing import Optional, Dict, Any
from app.services.game_engine.tools.memory_generator import MemoryGenerator
from app.models.character import Character
from app.models.scene import Scene
from app.db.session import Session


class MemoryManager:

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initializes the MemoryManager with a database session and a memory generator.
        """
        self.db_session = db_session
        self.memory_generator = MemoryGenerator(db_session=self.db_session)

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
                        memory_id = self.memory_generator.save_memory_to_db(memory, scene.id, character.id)
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