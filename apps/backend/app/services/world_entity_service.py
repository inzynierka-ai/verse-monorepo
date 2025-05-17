import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.services.llm import LLMService, ModelName
from app.utils.json_service import JSONService
from app.models.scene import Scene
from app.models.world_entity import WorldEntity as WorldEntityModel
from app.schemas.world_entity import WorldEntityFromLLM, WorldEntity
from app.crud.messages import get_messages_after_timestamp
from app.crud.stories import get_story_by_id
from app.crud.scenes import get_scene_by_uuid
from app.crud.world_entities import get_entity_names_by_story_id, get_related_entities, save_entity, get_entities_by_name

class WorldEntityService:
    def __init__(self, llm_service: Optional[LLMService] = None, db_session: Optional[Session] = None, story_id: Optional[int] = None):
        self.llm_service = llm_service or LLMService()
        self.db_session = db_session
        self.story = get_story_by_id(db_session, story_id) if db_session and story_id else None

    async def extract_entity_names(self, conversation_text: str) -> List[str]:
        """
        Extract potential world entity names (terms or concepts) from the scene.
        """
        if not conversation_text or conversation_text.strip() == "":
            logging.warning("Empty conversation text provided for entity extraction, returning empty list")
            return []
            
        system_prompt = """
        You are a language model assisting with building a game world's glossary.

        Given a transcript of a conversation, extract a list of terms that refer to:
        - organizations, places, technologies, slang, factions, religions, or cultural concepts
        - anything that characters in the world would "know about" or reference with shared meaning
        - only extract terms that are not general knowledge - e.g., clearly established outside of the game world
        - avoid common nouns or adjectives that are not specific to the world
        - avoid any terms that are not unique to the world or are too generic

        Return only the **distinct names** of the terms, not descriptions.

        Format: A JSON array of strings, e.g.:
        ["Arasaka", "The One Ring", "Death Star", "The Spice", "Anakin", "Horcruxes"]
        """

        messages = [
            self.llm_service.create_message("system", system_prompt),
            self.llm_service.create_message("user", f"Scene Transcript:\n{conversation_text}")
        ]

        try:
            response = await self.llm_service.generate_completion(
                messages=messages,
                model=ModelName.GEMINI_2_FLASH_LITE,
                temperature=0.3,
                stream=False
            )

            content = await self.llm_service.extract_content(response)
            
            if not content or content.strip() == "":
                logging.warning("Empty content returned from LLM for entity extraction, returning empty list")
                return []
                
            return JSONService.parse_and_validate_string_list(content)
        except Exception as e:
            logging.error(f"Error extracting entity names: {str(e)}")
            return []  # Return empty list on error rather than crashing
    
    async def get_relevant_world_entities(self, scene: Scene, last_message: str, last_message_embedding: List[float]) -> List[WorldEntity]:
        """
        Get relevant world entities based on the last message and scene context.
        
        This function performs three types of searches:
        1. Direct name matching: finds entities whose names or aliases match the extracted entity names
        2. Description matching: finds entities whose descriptions contain the extracted entity names
        3. Semantic similarity: finds entities whose embeddings are similar to the message embedding
        """
        if not self.db_session or not self.story:
            logging.warning("No DB session or story context available for entity retrieval")
            return []
            
        entities = []
        logging.info(f"Getting relevant world entities for story ID: {self.story.id}")
        
        # Step 1: Extract entity names from the message
        try:
            entity_names = await self.extract_entity_names(last_message)
            logging.info(f"Extracted entity names from message: {entity_names}")
        except Exception as e:
            logging.error(f"Error extracting entity names: {str(e)}")
            entity_names = []
        
        # Step 2a: Get entities by direct name match (name and aliases)
        name_match_count = 0
        if entity_names:
            for name in entity_names:
                try:
                    logging.info(f"Searching for entity by name/alias match: {name}")
                    name_entities = get_entities_by_name(
                        db=self.db_session,
                        query=name,
                        story_id=self.story.id,
                        search_descriptions=False  # Only search in names and aliases here
                    )
                    logging.info(f"Found {len(name_entities)} entities with name/alias matching '{name}'")
                    
                    for entity in name_entities:
                        try:
                            # Convert DB model to schema and add to results if not already there
                            entity_schema = WorldEntity.model_validate(entity.__dict__)
                            if entity_schema not in entities:
                                entities.append(entity_schema)
                                name_match_count += 1
                                logging.info(f"Added entity by name/alias match: {entity.name}")
                        except Exception as e:
                            logging.error(f"Error converting entity to schema: {str(e)}")
                            import traceback
                            logging.error(traceback.format_exc())
                except Exception as e:
                    logging.error(f"Error processing entity name '{name}': {str(e)}")
        
        logging.info(f"Found {name_match_count} entities by name/alias matching")
        
        # Step 2b: Get entities by description match - NEW FUNCTIONALITY
        desc_match_count = 0
        if entity_names:
            for name in entity_names:
                try:
                    logging.info(f"Searching for entity by description match: {name}")
                    desc_entities = get_entities_by_name(
                        db=self.db_session,
                        query=name,
                        story_id=self.story.id,
                        search_descriptions=True  # Search in descriptions
                    )
                    
                    # Filter to only include entities where the match is in the description
                    # (since this query might return entities that matched by name/alias as well)
                    description_matched_entities = []
                    for entity in desc_entities:
                        # Skip entities with name/alias matches (already processed)
                        if entity.name.lower().find(name.lower()) >= 0:
                            continue
                            
                        # Check if any alias contains the name
                        alias_match = False
                        if entity.aliases:
                            for alias in entity.aliases:
                                if alias.lower().find(name.lower()) >= 0:
                                    alias_match = True
                                    break
                        
                        if alias_match:
                            continue
                            
                        # If we get here, the entity matched by description
                        if entity.canonical_description.lower().find(name.lower()) >= 0:
                            description_matched_entities.append(entity)
                    
                    logging.info(f"Found {len(description_matched_entities)} entities with description containing '{name}'")
                    
                    for entity in description_matched_entities:
                        try:
                            # Convert DB model to schema and add to results if not already there
                            entity_schema = WorldEntity.model_validate(entity.__dict__)
                            if entity_schema not in entities:
                                entities.append(entity_schema)
                                desc_match_count += 1
                                logging.info(f"Added entity by description match: {entity.name} (description contains '{name}')")
                        except Exception as e:
                            logging.error(f"Error converting description-matched entity to schema: {str(e)}")
                            import traceback
                            logging.error(traceback.format_exc())
                except Exception as e:
                    logging.error(f"Error processing description search for '{name}': {str(e)}")
        
        logging.info(f"Found {desc_match_count} additional entities by description matching")
        
        # Step 3: Find semantically similar entities using the CRUD function (vector search)
        vector_match_count = 0
        if last_message_embedding:
            try:
                logging.info(f"Searching for semantically similar entities with threshold 0.3")
                vector_entities = get_related_entities(
                    db=self.db_session,
                    query_embedding=last_message_embedding,
                    story_id=self.story.id,
                    top_n=5,
                    similarity_threshold=0.3
                )
                logging.info(f"Found {len(vector_entities)} semantically similar entities")
                
                for entity in vector_entities:
                    try:
                        # Convert DB model to schema safely
                        entity_dict = {c.name: getattr(entity, c.name) 
                                    for c in entity.__table__.columns}
                        
                        # Handle embedding conversion if needed
                        if 'embedding' in entity_dict and entity_dict['embedding'] is not None:
                            if hasattr(entity_dict['embedding'], 'tolist'):
                                entity_dict['embedding'] = entity_dict['embedding'].tolist()
                        
                        entity_schema = WorldEntity(**entity_dict)
                        
                        if entity_schema not in entities:
                            entities.append(entity_schema)
                            vector_match_count += 1
                            logging.info(f"Added entity by vector similarity: {entity.name}")
                    except Exception as e:
                        logging.error(f"Error converting vector entity to schema: {str(e)}")
                        import traceback
                        logging.error(traceback.format_exc())
            except Exception as e:
                logging.error(f"Error retrieving vector entities: {str(e)}")
                import traceback
                logging.error(traceback.format_exc())
        else:
            logging.warning("No embedding provided for vector search")
        
        # Final summary logging
        logging.info(f"Found {name_match_count} entities by name matching")
        logging.info(f"Found {desc_match_count} entities by description matching")
        logging.info(f"Found {vector_match_count} entities by vector similarity")
        logging.info(f"Returning total of {len(entities)} relevant world entities")
        
        return entities

    def filter_known_entities(self, entity_names: List[str]) -> List[str]:
        """
        Filter out any entity names that are already defined in the database.
        """
        known = get_entity_names_by_story_id(self.db_session, self.story.id)
        return [name for name in entity_names if name.lower() not in {k.lower() for k in known}]

    async def describe_entity(self, entity_name: str, scene_text: str, related_entities: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        Generate a canonical description for a single world entity using scene and world context.
        Includes generation of 0-5 aliases for the entity.
        """
        if not self.story:
            logging.warning("No story context available for entity description")
            return None

        related_str = "\n".om([f"{e['name']}: {e['description']}" for e in related_entities])

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
        - The definition must only include information that would be *common* knowledge to characters in the world.
        - Especially, it must avoid referring to any characters or situations that are not famous or well-known in the world.
        - As this description will become canonical, feel free to use your own creativity to fill in the gaps where information is not present.
        - You are co-authoring the world with the user, so feel free to add your own creative flair.
        - Keep the style of the description consistent with the world and its lore.
        - Make the format encyclopedic, as if it were a Wikipedia entry - but brief and to the point.
        > Task 2:
        - Generate a list of 0-10 aliases for the term "{entity_name}".
        - These should be alternate names or terms that refer to the same entity.
        - Only include aliases that would naturally be used in the world
        - These could be shortened forms, slang terms, or formal/informal variations
        - Don't force aliases if none are appropriate
        
        > Output format:
        {{
            "name": "{entity_name}",
            "description": "Your generated description here.",
            "aliases": ["alias1", "alias2", "..."]
        }}
        """

        messages = [
            self.llm_service.create_message("system", system_prompt)
        ]

        try:
            response = await self.llm_service.generate_completion(
                messages=messages,
                model=ModelName.GEMINI_2_FLASH_LITE,
                temperature=0.4,
                stream=False
            )

            content = await self.llm_service.extract_content(response)
            logging.info(f"Entity description generated for '{entity_name}': {content[:100]}...")
            
            # Parse the response
            entity_data = JSONService.parse_and_validate_json_response(content, WorldEntityFromLLM)
            
            if entity_data and not hasattr(entity_data, 'aliases'):
                # Handle the case where LLM didn't include aliases in the response
                entity_data.aliases = []
            
            return entity_data
        except Exception as e:
            logging.error(f"Error generating entity description: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return None

    def save_entity_to_db(self, entity: WorldEntityFromLLM, scene: Optional[Scene] = None) -> Optional[int]:
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
                    
            # Convert scene.id to scene.uuid for discovered_in_scene field
            scene_uuid = scene.uuid if scene else None

            # Use the CRUD function to save the entity
            return save_entity(
                db=self.db_session,
                entity_data=entity,
                story_id=story_id,
                scene_uuid=scene_uuid
            )

        except Exception as e:
            logging.error(f"Failed to save world entity in service: {str(e)}")
            return None
    
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