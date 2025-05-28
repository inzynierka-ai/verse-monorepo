import logging
import json
from typing import List, AsyncGenerator, Dict, Any, Literal, Optional
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.services.platform.llm import LLMService, ModelName
from app.models.character import Character
from app.models.scene import Scene
from app.services.world.world_entity_service import WorldEntityService
from app.services.characters.memory_manager import MemoryManager
from datetime import datetime
from app.utils.embedding import optimize_text_for_embedding, get_embedding
from app.utils.json_service import JSONService
from app.schemas.conversation import ConversationTopic, ConversationTopicsResponse, ProcessingStatusMessage, ModerationResult, EntityExtractionResult, VectorSearchResult
import uuid
from langfuse.decorators import observe  # type: ignore

from app.services.platform.moderations import ModerationsService

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self):
        self.llm_service = LLMService()
        self.moderation_service = ModerationsService(
            openai_client=self.llm_service.openai_client)

    async def manage_websocket(self, websocket: WebSocket):
        """Context manager for WebSocket connection handling"""
        await websocket.accept()
        try:
            yield
        finally:
            await websocket.close()

    def verify_scene_id(self, message_scene_id: str, current_scene_id: str) -> bool:
        """Verify that the scene ID in the message matches the current scene ID"""
        return message_scene_id == current_scene_id

    @observe(name="process_message")
    async def process_message(self, db: Session, messages: List[Dict[str, Any]],
                              character: Character, scene: Scene, websocket: Optional[WebSocket] = None) -> AsyncGenerator[str, None]:
        """Process a message and generate a response"""
        import time

        latest_message = messages[-1]["content"]
        await self.save_message(
            db=db,
            scene_id=scene.id,
            character_id=character.id,
            content=latest_message,
            role="user"
        )

        # Step 1: Moderation
        if websocket:
            status_msg = ProcessingStatusMessage(
                type="processing_status",
                step="moderating",
                message="Checking content for safety..."
            )
            await websocket.send_text(status_msg.model_dump_json())

        start_time = time.time()
        violated_categories = await self.moderation_service.process_moderation(latest_message)
        moderation_time = (time.time() - start_time) * 1000

        if websocket:
            moderation_result = ModerationResult(
                is_flagged=bool(violated_categories),
                violated_categories=violated_categories,
                processing_time_ms=moderation_time
            )
            status_msg = ProcessingStatusMessage(
                type="processing_status",
                step="moderating",
                message="Content moderation complete",
                debug_info=moderation_result
            )
            await websocket.send_text(status_msg.model_dump_json())

        if violated_categories:
            logger.warning(f"Violated categories: {violated_categories}")

        # Step 2: Building prompt (includes entity extraction and vector search)
        if websocket:
            status_msg = ProcessingStatusMessage(
                type="processing_status",
                step="building_prompt",
                message="Building character context..."
            )
            await websocket.send_text(status_msg.model_dump_json())

        system_prompt = await self._build_character_prompt(db, character, scene, websocket)

        # Convert messages to the format expected by the LLM service
        formatted_messages = [
            self.llm_service.create_message("system", system_prompt)
        ]

        # Add conversation history
        for msg in messages:
            formatted_messages.append(
                self.llm_service.create_message(msg["role"], msg["content"]))

        # Step 3: Generate response
        if websocket:
            status_msg = ProcessingStatusMessage(
                type="processing_status",
                step="generating_response",
                message="Generating character response..."
            )
            await websocket.send_text(status_msg.model_dump_json())

        # Prepare arguments for LLM service
        llm_args: Dict[str, Any] = {
            "messages": formatted_messages,
            "model": ModelName.GPT41_MINI,
            "temperature": 0.7,
            "stream": True,
        }

        if violated_categories:
            llm_args["metadata"] = {
                "violated_categories": json.dumps(violated_categories)}

        # Get streaming response from LLM
        response = await self.llm_service.generate_completion(**llm_args)

        # Collect the full response while streaming chunks
        full_response = ""

        # Ensure we're always returning a generator
        if isinstance(response, AsyncGenerator):
            async def collect_and_stream() -> AsyncGenerator[str, None]:
                nonlocal full_response
                async for chunk in response:
                    full_response += chunk
                    yield chunk

                # Save the complete message after all chunks are processed
                await self.save_message(
                    db=db,
                    scene_id=scene.id,
                    character_id=character.id,
                    content=full_response,
                    role="assistant"
                )

            return collect_and_stream()
        else:
            # This branch should never be taken due to stream=True
            # but it's here to satisfy the type checker
            async def single_value_generator() -> AsyncGenerator[str, None]:
                response_text = str(response)
                yield response_text

                # Save the complete message
                await self.save_message(
                    db=db,
                    scene_id=scene.id,
                    character_id=character.id,
                    content=response_text,
                    role="assistant"
                )

            return single_value_generator()

    async def _build_character_prompt(self, db: Session, character: Character, scene: Scene, websocket: Optional[WebSocket] = None) -> str:
        """Build a system prompt for the character"""
        import time

        # Get location information
        story = scene.story
        logger.info(
            f"Building character prompt for {character.name} in scene {scene.uuid}")

        player_character = next(
            (char for char in scene.characters if char.role == "player"), None)
        player_name = player_character.name if player_character else "unknown player"
        logger.info(f"Player character identified as: {player_name}")

        # Entity extraction step
        if websocket:
            status_msg = ProcessingStatusMessage(
                type="processing_status",
                step="extracting_entities",
                message="Extracting entities from message..."
            )
            await websocket.send_text(status_msg.model_dump_json())

        start_time = time.time()
        optimized_last_message = await optimize_text_for_embedding(scene.messages[-1].content)
        logger.info(f"Last message: {optimized_last_message[:100]}...")
        last_message = scene.messages[-1].content
        last_message_embedding = get_embedding(optimized_last_message)
        logger.info(
            f"Generated embedding of length: {len(last_message_embedding) if last_message_embedding else 'None'}")

        # Extract entities for debug info
        world_entity_service = WorldEntityService(
            db_session=db, story_id=scene.story_id)  # type: ignore
        extracted_entities = await world_entity_service.extract_entity_names(last_message)
        entity_extraction_time = (time.time() - start_time) * 1000

        if websocket:
            entity_extraction_result = EntityExtractionResult(
                extracted_entities=extracted_entities,
                processing_time_ms=entity_extraction_time
            )
            status_msg = ProcessingStatusMessage(
                type="processing_status",
                step="extracting_entities",
                message=f"Extracted {len(extracted_entities)} entities",
                debug_info=entity_extraction_result
            )
            await websocket.send_text(status_msg.model_dump_json())

        # Vector search step
        if websocket:
            status_msg = ProcessingStatusMessage(
                type="processing_status",
                step="searching_vectors",
                message="Searching vector database for relevant context..."
            )
            await websocket.send_text(status_msg.model_dump_json())

        start_time = time.time()

        # Get character memories
        logger.info(f"Retrieving memories for character ID: {character.id}")
        memory_manager = MemoryManager(db_session=db)

        memories = await memory_manager.find_similar_memories(
            character_id=int(character.id),  # type: ignore
            query=last_message,
            top_n=5,
            similarity_threshold=0.3
        )
        logger.info(
            f"Retrieved {len(memories)} relevant memories for character {character.name}")

        # Get relevant world entities with detailed logging
        logger.info(f"Retrieving world entities for story ID: {scene.story_id}")

        try:
            logger.info(
                f"Calling get_relevant_world_entities with message length {len(optimized_last_message)} and embedding length {len(last_message_embedding) if last_message_embedding else 'None'}")
            world_entities = await world_entity_service.get_relevant_world_entities(
                scene,
                optimized_last_message,
                last_message_embedding
            )

            # Log details about the retrieved entities
            logger.info(
                f"Retrieved {len(world_entities) if world_entities else 0} world entities")
            for i, entity in enumerate(world_entities if world_entities else []):
                logger.info(
                    f"Entity {i+1}: {entity.name} - {entity.canonical_description[:50]}...")
        except Exception as e:
            logger.error(f"Error retrieving world entities: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            world_entities = []

        vector_search_time = (time.time() - start_time) * 1000

        # Send vector search results
        if websocket:
            # Format entities for debug info
            entities_debug = []
            for entity in world_entities or []:
                entities_debug.append({
                    "name": entity.name,
                    "description": entity.canonical_description[:100] + "..." if len(entity.canonical_description) > 100 else entity.canonical_description,
                    "aliases": entity.aliases
                })

            # Format memories for debug info
            memories_debug = []
            for memory in memories or []:
                memory_text = getattr(memory, 'memory_text', '') or ""
                memories_debug.append({  # type: ignore
                    "text": memory_text[:100] + "..." if len(memory_text) > 100 else memory_text
                })

            vector_search_result = VectorSearchResult(
                entities_found=entities_debug,  # type: ignore
                memories_found=memories_debug,  # type: ignore
                name_matches=0,  # These would need to be tracked in the world entity service
                description_matches=0,
                vector_matches=len(world_entities or []),
                total_results=len(world_entities or []) + len(memories or []),
                processing_time_ms=vector_search_time
            )
            status_msg = ProcessingStatusMessage(
                type="processing_status",
                step="searching_vectors",
                message=f"Found {len(world_entities or [])} entities, {len(memories or [])} memories",
                debug_info=vector_search_result
            )
            await websocket.send_text(status_msg.model_dump_json())

        # Log location info
        location_info = f"You are currently at {scene.location.name}. {scene.location.description}" if scene.location else ""
        logger.info(
            f"Location info: {location_info[:100]}..." if location_info else "No location info")

        # Prepare world entities section with error handling
        try:
            if world_entities and len(world_entities) > 0:
                entities_text_list = []
                for entity in world_entities:
                    # Format each entity with name, description and aliases if any
                    entity_text = f"- {entity.name}: {entity.canonical_description}"

                    # Add aliases if they exist
                    if entity.aliases and len(entity.aliases) > 0:
                        alias_text = ", ".join(entity.aliases)
                        entity_text += f" (Also known as: {alias_text})"

                    entities_text_list.append(entity_text)  # type: ignore

                entities_text = chr(10).join(entities_text_list)  # type: ignore
                logger.info(f"Including {len(world_entities)} world entities in prompt")
            else:
                entities_text = "None"
                logger.info("No world entities to include in prompt")
        except Exception as e:
            logger.error(f"Error formatting world entities: {str(e)}")
            entities_text = "None"

        # Prepare memories section with error handling
        try:
            if memories and len(memories) > 0:
                memories_text = chr(10).join(
                    [f"- {memory.memory_text}" for memory in memories])
                logger.info(f"Including {len(memories)} memories in prompt")
            else:
                memories_text = "None"
                logger.info("No memories to include in prompt")
        except Exception as e:
            logger.error(f"Error formatting memories: {str(e)}")
            memories_text = "None"

        character_prompt = f"""
        You are not a language model. You are a fully realized character in a fictional story titled "{story.title}".

        Your name is {character.name}. Here is your character description:
        {character.description}

        Your backstory:
        {character.backstory}

        Your personality traits:
        {character.personality_traits}  

        Your goals in the story:
        {character.goals}

        Your speaking style:
        {character.speaking_style}

        Your immediate goals for the current situation (These are very important and you should focus on achieving them now):
        {character.immediate_goals}

        You are in the following situation:
        {scene.description}

        You are currently speaking with the player character named {player_name}. Speak and act according to your personality, goals, and knowledge. Do **not** narrate or explain your behavior unless it's something your character would naturally do.

        Memories of past interactions (which you remember as real experiences):
        {memories_text}
        
        Your current location:
        {location_info}

        Relevant world entities and lore:
        {entities_text}

        Strict Rules:
        - Stay completely in character. Never refer to being an AI, LLM, or model.
        - Use language, tone, and knowledge consistent with your role in the story world.
        - Do not break the fourth wall.
        - Do not provide options, summaries, or meta-commentary unless it's something your character would naturally do.
        - Respond as if this world is real to you. Stay grounded in the current situation and your personality.
        - Do not make your part too long. Keep it really concise to maintain a quick back-and-forth with the player.
        - Avoid finishing senteces with questions.
        """

        return character_prompt

    @observe(name="generate_conversation_topics")
    async def generate_conversation_topics(self, db: Session, character: Character, scene: Scene, messages: Optional[List[Dict[str, Any]]] = None) -> ConversationTopicsResponse:
        """Generate conversation topics for a character in a specific scene"""

        try:
            # Get player character info
            player_character = next(
                (char for char in scene.characters if char.role == "player"), None)
            player_name = player_character.name if player_character else "unknown player"

            # Prepare location information
            location_info = f"You are currently at {scene.location.name}. {scene.location.description}" if scene.location else ""

            # Get previous scene summary if available and fetch previous messages
            previous_scene_context = ""
            previous_scene = None
            try:
                from app.crud.scenes import get_latest_completed_scene_by_story
                # Extract the actual integer value from the scene.story_id column
                story_id = int(scene.story_id)  # type: ignore
                previous_scene = get_latest_completed_scene_by_story(db, story_id)
                if previous_scene and getattr(previous_scene, 'summary', None):
                    summary_text = str(previous_scene.summary)
                    # previous_scene.messages
                    previous_scene_context = f"\nPrevious scene summary: {summary_text}"
                    logger.info(
                        f"Including previous scene summary: {summary_text[:100]}...")
            except Exception as e:
                logger.warning(f"Could not fetch previous scene summary: {str(e)}")

            # Prepare message history context
            message_history_context = ""
            all_messages: List[Dict[str, Any]] = []

            # First, get previous messages from the last scene with this character if available (limited)
            if previous_scene is not None:
                try:
                    from app.crud.messages import get_messages_by_scene_and_character
                    # Convert Column objects to string values
                    prev_scene_uuid = str(previous_scene.uuid)
                    character_uuid = str(character.uuid)
                    prev_messages = get_messages_by_scene_and_character(
                        db, prev_scene_uuid, character_uuid)
                    # Limit previous scene messages to last 3 to avoid overwhelming the prompt
                    limited_prev_messages = prev_messages[-3:] if len(
                        prev_messages) > 3 else prev_messages
                    # Convert to the format expected (dict with role and content)
                    for msg in limited_prev_messages:
                        all_messages.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                    logger.info(
                        f"Retrieved {len(limited_prev_messages)} messages from previous scene (out of {len(prev_messages)} total)")
                except Exception as e:
                    logger.warning(f"Could not fetch previous messages: {str(e)}")

            # Add ALL current messages if provided (no limitation)
            if messages and len(messages) > 0:
                all_messages.extend(messages)
                logger.info(f"Added {len(messages)} current messages")

            # Prepare last message analysis and conversation hooks
            last_message_analysis = ""

            # Use all messages for context (no additional limitation)
            if all_messages:
                message_texts: List[str] = []
                for msg in all_messages:
                    role = "Player" if msg.get("role") == "user" else character.name
                    content = msg.get("content", "")
                    message_texts.append(f"{role}: {content}")

                if message_texts:
                    message_history_context = f"\nRecent conversation:\n" + \
                        "\n".join(message_texts)
                    logger.info(
                        f"Including {len(all_messages)} total messages in context")

                # Extract and analyze the very last message for hooks
                if len(all_messages) > 0:
                    last_msg = all_messages[-1]
                    last_role = "Player" if last_msg.get(
                        "role") == "user" else character.name
                    last_content = last_msg.get("content", "")
                    last_message_analysis = f"\nLAST MESSAGE ANALYSIS:\n{last_role}: \"{last_content}\""

            # Determine if this is a first interaction or continuation
            is_first_interaction = not all_messages or len(all_messages) == 0

            if is_first_interaction:
                system_prompt = f"""You are a conversation topic generator for a narrative text adventure game that creates natural conversation starters for a player meeting a character.
                PRIMARY GOAL: Generate 3 conversation starter topics that the player can use to initiate their first interaction with {character.name}. These should feel natural and appropriate for their current relationship level and the situation.

FIRST INTERACTION STRATEGY:
1. **Relationship-Appropriate**: Consider the current relationship level ({character.relationship_level}/100) when suggesting conversation starters
2. **Context-Aware**: Use the current scene, location, and story context to suggest relevant topics
3. **Character-Specific**: Topics should reflect what would naturally interest or engage {character.name}
4. **Natural Greetings**: Include appropriate greeting styles based on relationship level and character personality
5. **Scene Integration**: Use elements from the current scene to create natural conversation hooks

RELATIONSHIP LEVEL GUIDELINES:
- **Low (0-30)**: Formal introductions, polite observations about the environment, safe topics
- **Medium (31-70)**: Friendly greetings, shared experiences, casual questions about their day/situation
- **High (71-100)**: Warm greetings, personal check-ins, intimate or deeper conversation topics

CONVERSATION STARTER TYPES:
- **Greeting + Observation**: "Hello! This place seems quite [interesting/busy/peaceful]..."
- **Situational Comment**: Reference something happening in the current scene or location
- **Character Interest**: Ask about something related to their description or role
- **Shared Context**: Reference the story situation you're both experiencing
- **Polite Inquiry**: Ask how they're doing or feeling about the current situation

Examples based on relationship level:
- **Strangers (0-30)**: "Hello, I don't think we've met. I'm {player_name}."
- **Acquaintances (31-70)**: "Hey there! How are you finding this place?"
- **Friends (71-100)**: "Hi! I was hoping I'd run into you here."

For each topic, provide:
1. A short title (2-3 words maximum)
2. A natural conversation starter message

Return your response as a JSON array of objects with "title" and "message" fields:
[
  {{"title": "Greeting", "message": "Hello! I don't think we've properly met yet."}},
  {{"title": "The Scene", "message": "This place is quite interesting, isn't it?"}},
  {{"title": "Their Role", "message": "I've heard you're involved with [relevant topic]. How's that going?"}}
]

Keep titles very short and messages natural and conversational.

Character Information:
- Name: {character.name}
- Description: {character.brief_description}
- Relationship Level with {player_name}: {character.relationship_level}/100

Current Situation:
- Story: {scene.story.title}
- Scene: {scene.description}
- Location: {location_info}{previous_scene_context}
"""
            else:
                system_prompt = f"""You are a conversation topic generator for a narrative text adventure game that creates natural, flowing conversation topics based on the most recent interaction.
                PRIMARY GOAL: Generate 3 conversation topics that naturally flow from the LAST MESSAGE above. These should feel like organic responses that {character.name} would naturally think to explore.

TOPIC GENERATION STRATEGY:
1. **Last Message Priority**: Focus heavily on the most recent exchange - what was said, what wasn't said, and what emotions/subtext were present
2. **Natural Flow**: Topics should feel like they directly follow from the conversation, not random new subjects
3. **Character Voice**: Each topic should reflect what {character.name} would genuinely be curious about or want to explore
4. **Emotional Intelligence**: Pick up on emotional cues, unspoken concerns, or underlying tensions
5. **Relationship Building**: Use the conversation momentum to deepen understanding between characters

CRITICAL REQUIREMENTS:
- **Hook Analysis**: Identify specific elements from the last message that can be expanded upon
- **Emotional Resonance**: Look for feelings, concerns, or interests that weren't fully explored
- **Natural Transitions**: Topics should feel like the next logical step in the conversation
- **Character Motivation**: Consider what {character.name} would genuinely want to know or discuss
- **Avoid Generic**: Don't suggest broad topics unless they directly relate to what was just discussed

CONVERSATION HOOKS TO EXPLORE FROM LAST MESSAGE:
Analyze the last message for these potential conversation starters:
- Emotions expressed or hinted at that could be explored
- Unfinished thoughts or statements that trail off
- Questions asked that could be expanded upon
- Concerns, fears, or worries mentioned
- Achievements, successes, or positive moments that could be celebrated
- References to past events that could be discussed further
- Contradictions or inconsistencies that could be gently questioned
- Body language, tone, or subtext that {character.name} would pick up on
- Information gaps that {character.name} might be curious about
- Opportunities for {character.name} to share similar experiences or relate

Examples of GOOD conversation hooks:
- If someone mentions being tired → "You seem exhausted, what's been keeping you up?"
- If someone hesitates before speaking → "You looked like you wanted to say something else..."
- If someone mentions a person → "Tell me more about [that person], they sound important to you"
- If someone shows emotion → "I can see this really matters to you..."

For each topic, provide:
1. A short title (2-3 words maximum)
2. A message that naturally follows from the conversation

Return your response as a JSON array of objects with "title" and "message" fields:
[
  {{"title": "Their Plans", "message": "What are you planning to do after this?"}},
  {{"title": "Strange Noise", "message": "Did you hear that odd sound earlier? It seemed to come from the corridor."}},
  {{"title": "Compliment", "message": "I really like your outfit today, it suits you well."}}
]

Keep titles very short and messages natural and conversational.

Character Information:
- Name: {character.name}
- Description: {character.brief_description}
- Relationship Level with {player_name}: {character.relationship_level}/100

Current Situation:
- Story: {scene.story.title}
- Scene: {scene.description}
- Location: {location_info}{previous_scene_context}{message_history_context}{last_message_analysis}
"""

            messages = [
                self.llm_service.create_message("system", system_prompt)
            ]

            response = await self.llm_service.generate_completion(
                messages=messages,
                model=ModelName.GPT41_MINI,
                temperature=0.8,
                max_tokens=500
            )

            # Handle streaming response
            content: str = ""
            if hasattr(response, "__aiter__"):
                content = await self.llm_service.extract_content(response)
            else:
                content = str(response)

            # Use JSONService to parse and validate the response
            try:
                topics_list = JSONService.parse_and_validate_json_list(
                    content, ConversationTopic)
                # Limit to 3 topics as specified in the prompt
                topics_list = topics_list[:3]

            except ValueError as e:
                logger.error(f"Failed to parse or validate topics JSON: {str(e)}")
                logger.error(f"Raw content: {content}")
                topics_list = []

            return ConversationTopicsResponse(topics=topics_list)

        except Exception as e:
            logger.error(
                f"Error generating conversation topics for character {character.name}: {str(e)}")
            # Return empty topics list on error
            return ConversationTopicsResponse(topics=[])

    async def save_message(self, db: Session, scene_id: Any,
                           character_id: Any, content: str, role: Literal["user", "assistant", "system"]) -> Dict[str, Any]:
        """Save a message to the database"""
        from app.crud.messages import create_message
        from app.schemas.message import MessageCreate

        # Make sure we have integer values for IDs
        # This safely handles both direct integers and SQLAlchemy Column/objects
        scene_id_value = getattr(scene_id, "value", scene_id)
        if hasattr(scene_id, "id"):
            scene_id_value = scene_id.id

        character_id_value = getattr(character_id, "value", character_id)
        if hasattr(character_id, "id"):
            character_id_value = character_id.id

        message = MessageCreate(
            scene_id=scene_id_value,
            character_id=character_id_value,
            content=content,
            role=role,
            timestamp=datetime.now(),
            uuid=str(uuid.uuid4())
        )

        return create_message(db, message)
