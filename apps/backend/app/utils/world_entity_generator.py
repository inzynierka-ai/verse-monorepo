import logging
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.services.llm import LLMService, ModelName
from app.utils.embedding import get_embedding
from app.utils.json_service import JSONService
from app.models.world_entity import WorldEntity as WorldEntityModel
from app.crud.messages import get_messages_by_scene
from app.crud.world_entities import get_all_entity_names, get_related_entities


class WorldEntityGenerator:
    def __init__(self, llm_service: Optional[LLMService] = None, db_session: Optional[Session] = None):
        self.llm_service = llm_service or LLMService()
        self.db_session = db_session

    async def extract_entity_names(self, scene_id: int) -> List[str]:
        """
        Extract potential world entity names (terms or concepts) from the scene.
        """
        conversation = get_messages_by_scene(scene_id)
        if not conversation:
            return []

        conversation_text = "\n".join([f"{msg.character.name}: {msg.content}" for msg in conversation])

        system_prompt = """
        You are a language model assisting with building a game world's glossary.

        Given a transcript of a conversation, extract a list of terms that refer to:
        - organizations, places, technologies, slang, factions, religions, or cultural concepts
        - anything that characters in the world would "know about" or reference with shared meaning

        Return only the **distinct names** of the terms, not descriptions.

        Format: A JSON list of strings, e.g.:
        ["Arasaka", "cyberware", "The Slums", "EdgeNet", "Biowitchers"]
        """

        messages = [
            self.llm_service.create_message("system", system_prompt),
            self.llm_service.create_message("user", f"Scene Transcript:\n{conversation_text}")
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_FLASH_LITE,
            temperature=0.3,
            stream=False
        )

        content = await self.llm_service.extract_content(response)
        return JSONService.parse_and_validate_string_list(content)

    def filter_known_entities(self, entity_names: List[str]) -> List[str]:
        """
        Filter out any entity names that are already defined in the database.
        """
        known = get_all_entity_names(self.db_session)
        return [name for name in entity_names if name.lower() not in {k.lower() for k in known}]

    async def describe_entity(self, entity_name: str, scene_text: str, related_entities: List[Dict]) -> Optional[Dict]:
        """
        Generate a canonical description for a single world entity using scene and world context.
        """
        related_str = "\n".join([f"{e['name']}: {e['description']}" for e in related_entities])

        system_prompt = f"""
        You are building a glossary entry for the term "{entity_name}" in a fictional game world.

        The term was encountered in this scene:
        ---
        {scene_text}
        ---

        Here are known, related world concepts:
        {related_str if related_entities else 'None'}

        Task:
        - Write a short canonical description (1–3 sentences) that could be added to a world glossary.
        - Be concise, specific, and avoid repeating known concepts.
        - Assume the reader is a character in the world who already knows general context.

        Output format:
        {{
            "name": "{entity_name}",
            "description": "Your generated description here."
        }}
        """

        messages = [
            self.llm_service.create_message("system", system_prompt)
        ]

        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_FLASH_LITE,
            temperature=0.4,
            stream=False
        )

        content = await self.llm_service.extract_content(response)
        return JSONService.parse_and_validate_single_object(content, required_keys=["name", "description"])

    def save_entity_to_db(self, entity: dict, scene_id: Optional[int] = None) -> Optional[int]:
        try:
            embedding = get_embedding(entity["description"])

            db_entity = WorldEntityModel(
                name=entity["name"],
                canonical_description=entity["description"],
                embedding=embedding,
                discovered_in_scene=scene_id
            )

            if self.db_session:
                self.db_session.add(db_entity)
                self.db_session.commit()
                logging.info(f"Saved new world entity: {entity['name']}")
                return db_entity.id
            else:
                logging.error("No DB session available, could not save world entity.")
                return None

        except Exception as e:
            logging.error(f"Failed to save world entity: {str(e)}")
            if self.db_session and self.db_session.is_active:
                self.db_session.rollback()
            raise

    async def process_scene_entities(self, scene_id: int) -> List[int]:
        """
        Full pipeline: extract names, filter known, describe new, and save them.
        Returns a list of saved entity IDs.
        """
        conversation = get_messages_by_scene(scene_id)
        if not conversation:
            return []

        scene_text = "\n".join([f"{msg.character.name}: {msg.content}" for msg in conversation])
        detected_names = await self.extract_entity_names(scene_id)
        new_names = self.filter_known_entities(detected_names)

        saved_ids = []

        for name in new_names:
            related = get_related_entities(self.db_session, name)
            description_data = await self.describe_entity(name, scene_text, related)

            if description_data:
                entity_id = self.save_entity_to_db(description_data, scene_id=scene_id)
                if entity_id:
                    saved_ids.append(entity_id)

        return saved_ids
