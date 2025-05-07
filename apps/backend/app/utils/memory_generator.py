import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from app.schemas.message import Message
from app.crud.messages import get_messages_by_scene
from app.services.llm import LLMService, ModelName
from app.utils.json_service import JSONService
from app.models.character_memory import CharacterMemory as CharacterMemoryModel
from app.utils.embedding import get_embedding


class MemoryGenerator:
    """
    Service for generating character memories from conversation messages.
    """
    def __init__(self, llm_service: Optional[LLMService] = None, db_session: Optional[Session] = None):
        self.llm_service = llm_service or LLMService()
        self.db_session = db_session

    async def extract_memories(self, scene_id:int) -> List[str]:
        """
        Extracts memories from the conversation messages.
        """
        conversation = get_messages_by_scene(scene_id)
        if not conversation:
            return []     

        character_name = conversation[0].character.name
        conversation_text = "\n".join([f"{msg}\n" for msg in conversation])

        system_prompt = f"""
                    You are an AI assistant who helps generate memory summaries for game characters.

                    Below is a transcript of a conversation between a player and a character named **{character_name}**, who is an NPC in an interactive story.

                    Your task is to extract the **most important memories that {character_name} would retain from this interaction**.

                    A memory is something the character would remember later — such as:
                    - Important facts the player revealed
                    - Emotional impressions
                    - Promises, threats, gifts, or betrayals
                    - The nature of the relationship (friendship, hostility, admiration)
                    - Key questions or mysteries discussed
                    - Places or items mentioned with significance

                    Please return a list of **concise memory statements** from {{character_name}}'s point of view, using first-person (e.g., "The player helped me..." or "I now trust them less...").

                    Only include things that are truly meaningful or likely to affect future interactions.
                    
                    Format your response as a JSON array of strings, where each string contains a distinct memory statement.
                    Example format:
                    [
                        "I learned that the player is looking for a rare artifact.",
                        "The player promised to help me find my lost sister.",
                        "I felt betrayed when the player revealed my secret."
                    ]

                """
                
        messages = [
            self.llm_service.create_message("system", system_prompt),
            self.llm_service.create_message("user", f"Transcript: {conversation_text}"),
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_FLASH_LITE,
            temperature=0.5,
            stream=False
        )

        content = await self.llm_service.extract_content(response)
        memories = JSONService.parse_and_validate_string_list(content)
        return memories
    
    def _save_memory_to_db(self, memory: str, scene_id:int, character_id: int) -> None:
        """
        Save the generated memories to the database.
        """

        try:
            # create a database model from the memory
            db_memory = CharacterMemoryModel(   
                character_id=character_id,
                scene_id=scene_id,
                memory_text=memory,
                embedding=get_embedding(memory)
            )

            #add the memory to the session
            if self.db_session:
                self.db_session.add(db_memory)
                self.db_session.commit()
                logging.info(f"Memory saved to DB: {memory}")
                memory_id = db_memory.id
                return memory_id
            else:
                logging.error("No database session available, memory not saved to database")
                return None
        except Exception as e:
            logging.error(f"Failed to save memory to database: {str(e)}")
            if self.db_session is not None and hasattr(self.db_session, 'is_active') and self.db_session.is_active:
                self.db_session.rollback()
            raise