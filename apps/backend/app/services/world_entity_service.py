import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.llm import LLMService, ModelName
from app.utils.embedding import get_embedding
from app.utils.json_service import JSONService
from app.models.world_entity import WorldEntity as WorldEntityModel
from app.models.message import Message
from app.models.scene import Scene
from app.models.story import Story
from app.crud.messages import get_messages_by_scene, get_messages_after_timestamp
from app.crud.stories import get_story_by_id
from app.crud.scenes import get_scene_by_uuid
from app.crud.world_entities import get_entity_names_by_story_id, get_related_entities


class WorldEntityService:
    def __init__(self, llm_service: Optional[LLMService] = None, db_session: Optional[Session] = None, story_id: Optional[int] = None):
        self.llm_service = llm_service or LLMService()
        self.db_session = db_session
        self.story = get_story_by_id(db_session, story_id) if db_session and story_id else None

    async def extract_entity_names(self, conversation_text: str) -> List[str]:
        """
        Extract potential world entity names (terms or concepts) from the scene.
        """
        system_prompt = """
        You are a language model assisting with building a game world's glossary.

        Given a transcript of a conversation, extract a list of terms that refer to:
        - organizations, places, technologies, slang, factions, religions, or cultural concepts
        - anything that characters in the world would "know about" or reference with shared meaning

        Return only the **distinct names** of the terms, not descriptions.

        Format: A JSON list of strings, e.g.:
        ["Arasaka", "London", "The One Ring", "Death Star", "The Spice", "Anakin", "Horcruxes"]
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
        known = get_entity_names_by_story_id(self.db_session, self.story.id)
        return [name for name in entity_names if name.lower() not in {k.lower() for k in known}]

    async def describe_entity(self, entity_name: str, scene_text: str, related_entities: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        Generate a canonical description for a single world entity using scene and world context.
        """
        if not self.story:
            logging.warning("No story context available for entity description")
            return None

        related_str = "\n".join([f"{e['name']}: {e['description']}" for e in related_entities])

        system_prompt = f"""
        > You are building a glossary entry for the term "{entity_name}" in a fictional game world.

        > This game world has its own unique lore, characters, and settings. The term "{entity_name}" is a concept or term that characters in the world would know about.

        > Here is the description of the world/story:
        {self.story.description}

        > The term was encountered in this scene:
        ---
        {scene_text}
        ---

        > Here are known, related world concepts:
        {related_str if related_entities else 'None'}

        > Task:
        - Write a short canonical description (1–3 sentences) that could be added to a world glossary.
        - Be concise, specific, and avoid repeating known concepts.
        - Assume the reader is a character in the world who already knows general context.
        - The term must be defined in a way that is useful for all characters in the world.
        - The definition must only include information that would be common knowledge to characters in the world.
        - Especially, it must avoid referring to any characters or situations that are not famous or well-known in the world.
        - As this description will become canonical, feel free to use your own creativity to fill in the gaps where information is not present.
        - You are co-authoring the world with the user, so feel free to add your own creative flair.
        - Keep the style of the description consistent with the world and its lore.
        - Make the format encyclopedic, as if it were a Wikipedia entry - but brief and to the point.

        > Output format:
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

    def save_entity_to_db(self, entity: Dict[str, str], scene: Optional[Scene] = None) -> Optional[int]:
        """
        Save an entity to the database.
        
        Args:
            entity: Dictionary with 'name' and 'description' keys
            scene: Scene object the entity was discovered in (optional)
            
        Returns:
            Entity ID if saved successfully, None otherwise
        """
        if not self.db_session:
            logging.error("No DB session available, could not save world entity.")
            return None

        try:
            story_id = scene.story_id if scene else (self.story.id if self.story else None)
            if not story_id:
                logging.error("No story ID available, cannot save entity.")
                return None
                
            embedding = get_embedding(entity["description"])
            
            # Convert scene.id to scene.uuid for discovered_in_scene field
            scene_uuid = scene.uuid if scene else None

            # Explicitly set the created_at timestamp to ensure it's not NULL
            current_time = datetime.utcnow()

            db_entity = WorldEntityModel(
                name=entity["name"],
                canonical_description=entity["description"],
                embedding=embedding,
                discovered_in_scene=scene_uuid,
                story_id=story_id,
                created_at=current_time,
            )

            self.db_session.add(db_entity)
            self.db_session.commit()
            logging.info(f"Saved new world entity: {entity['name']} at {current_time}")
            return db_entity.id

        except Exception as e:
            logging.error(f"Failed to save world entity: {str(e)}")
            if self.db_session and self.db_session.is_active:
                self.db_session.rollback()
            raise
    
    async def process_new_scene_entities(self, scene_uuid: str) -> List[int]:
        """
        Process only new messages since the last time this scene was analyzed.
        
        Args:
            scene_uuid: UUID of the scene to process
            
        Returns:
            List of IDs of saved entities
        """
        if not self.db_session:
            logging.error("No DB session available, cannot process scene entities.")
            return []

        # Get scene information
        scene = get_scene_by_uuid(self.db_session, scene_uuid)
        if not scene:
            logging.warning(f"Scene with UUID {scene_uuid} not found.")
            return []
            
        # Set story context if needed
        if not self.story:
            self.story = get_story_by_id(self.db_session, scene.story_id)

        # Find the newest entity discovered in this scene
        last_entity_query = (
            self.db_session.query(WorldEntityModel)
            .filter(WorldEntityModel.discovered_in_scene == scene_uuid)
            .order_by(WorldEntityModel.created_at.desc())
        )
        
        last_processed_entity = last_entity_query.first()
        if last_processed_entity:
            logging.info(f"Last processed entity: {last_processed_entity.name} at {last_processed_entity.created_at}")
        else:
            logging.info("No previously processed entities found for this scene.")
        
        # Get messages since last processing time (if available)
        last_processed_time = last_processed_entity.created_at if last_processed_entity and hasattr(last_processed_entity, 'created_at') else None
        
        # Use the new common function to get messages after timestamp
        messages = get_messages_after_timestamp(db=self.db_session, scene_uuid=scene_uuid, timestamp=last_processed_time)
        
        # Log appropriate message based on whether we're using a timestamp filter
        if last_processed_time:
            logging.info(f"Processing {len(messages)} new messages since {last_processed_time}")
        else:
            logging.info(f"Processing all {len(messages)} messages (first run)")
        
        if not messages:
            logging.info(f"No new messages to process for scene {scene_uuid}.")
            return []

        # Format messages into conversation text
        conversation_text = "\n".join([str(msg) for msg in messages])

        # Continue with existing processing logic
        detected_names = await self.extract_entity_names(conversation_text=conversation_text)
        new_names = self.filter_known_entities(detected_names)
        
        if not new_names:
            logging.info(f"No new entities found in scene {scene_uuid}.")
            return []
        
        logging.info(f"Detected new entities: {new_names}")

        saved_ids = []
        for name in new_names:
            related = get_related_entities(self.db_session, name, self.story.id)
            description_data = await self.describe_entity(name, conversation_text, related)

            if description_data:
                entity_id = self.save_entity_to_db(description_data, scene=scene)
                if entity_id:
                    saved_ids.append(entity_id)

        return saved_ids