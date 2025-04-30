import asyncio
import logging
from typing import Optional, Any, List, Dict
import uuid

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.models.scene import Scene as SceneModel
from app.models.character import Character as CharacterOrmModel
from app.models.location import Location as LocationOrmModel
from app.services.scene_service import SceneService
from app.services.scene_generator import SceneGeneratorAgent
from app.services.llm import LLMService
from app.crud.stories import get_story_by_uuid
from app.models.story import Story
from app.schemas.story import StoryRead
from app.schemas.story_generation import (
    Story as StoryGenerationSchema,
    Character as CharacterGenerationSchema,
    Location as LocationGenerationSchema
)
from app.utils.model_converters import convert_character, convert_characters, convert_locations
from app.schemas.scene_generator import SceneGenerationResult

logger = logging.getLogger(__name__)


class SceneGenerationHandler:
    """
    Manages the scene generation process for a single WebSocket connection.
    """

    def __init__(
        self,
        websocket: WebSocket,
        story_uuid: uuid.UUID,
        db_session: Session,
        user_id: int
    ):
        self.websocket = websocket
        self.story_uuid = story_uuid
        self.db_session = db_session
        self.user_id = user_id
        self.scene_service = SceneService()
        self.llm_service = LLMService()
        self.agent: Optional[SceneGeneratorAgent] = None
        self.agent_task: Optional[asyncio.Task[Any]] = None
        self.active_actions: Dict[str, str] = {}

    async def run(self):
        """
        Main logic loop for the handler. Checks for existing scenes and runs the agent.
        """
        try:
            logger.info(f"SceneGenerationHandler started for story {self.story_uuid}")

            story_orm = self._get_story()
            story_data = StoryRead.model_validate(story_orm)

            story_internal_id = story_data.id
            latest_scene = self._fetch_latest_scene(story_internal_id)

            if latest_scene and self._is_scene_complete(latest_scene):
                logger.info(f"Found complete scene {latest_scene.id} for story {self.story_uuid}")
                await self._send_scene_complete(latest_scene)
            else:
                logger.info(f"No complete scene found for story {self.story_uuid}. Starting generation.")
                await self._run_generation(story_data, story_orm)

            while True:
                await asyncio.sleep(1)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for story {self.story_uuid}. Cleaning up.")
            await self._cleanup()
        except PermissionError as e:
            logger.warning(f"Permission denied for story {self.story_uuid}: {e}")
            await self._send_error(str(e))
            await self._cleanup()
        except ValueError as e:
            logger.error(f"Data error for story {self.story_uuid}: {e}")
            await self._send_error(f"Internal data error: {str(e)}")
            await self._cleanup()
        except Exception as e:
            logger.exception(f"Error in SceneGenerationHandler for story {self.story_uuid}: {e}")
            await self._send_error(f"An unexpected error occurred: {str(e)}")
            await self._cleanup()

    def _get_story(self) -> Story:
        """Fetches the story using the UUID and handles errors."""
        try:
            story = get_story_by_uuid(
                self.db_session,
                self.story_uuid,
                self.user_id
            )
            if not story:
                raise PermissionError("Story not found or access denied.")
            return story
        except PermissionError:
            raise
        except Exception as e:
            logger.exception(f"Database error fetching story {self.story_uuid}: {e}")
            raise RuntimeError(f"Failed to retrieve story data due to database error: {e}")

    def _fetch_latest_scene(self, story_id: int) -> Optional[SceneModel]:
        """Fetches the latest scene from the database using the internal story ID."""
        try:
            return self.scene_service.fetch_latest_scene(self.db_session, story_id)
        except Exception as e:
            logger.exception(f"Database error fetching latest scene for story ID {story_id}: {e}")
            raise

    def _is_scene_complete(self, scene: SceneModel) -> bool:
        """Checks if a fetched scene is considered complete."""
        return bool(scene.description)

    async def _run_generation(self, story_data: StoryRead, story_orm: Story):
        """Instantiates and runs the SceneGeneratorAgent."""
        try:
            logger.info(f"Starting generation for story: {story_data.title} ({story_data.uuid})")

            player_character_orm = next((char for char in story_orm.characters if char.role == 'player'), None)

            if not player_character_orm:
                logger.error(f"Player character not found for story {story_data.uuid}. Cannot proceed.")
                raise ValueError("Player character is required for scene generation but was not found.")
            logger.info(f"Player character orm: {player_character_orm}")
            
            # Use the new converter utility
            player_character_schema = convert_character(player_character_orm)
            logger.info(f"Player character schema: {player_character_schema}")

            generation_input_story = StoryGenerationSchema(
                title=story_data.title,
                description=story_data.description or "",
                rules=story_data.rules.split('\n') if story_data.rules else [],
                user_id=story_data.user_id,
                uuid=story_data.uuid,
                id=story_data.id
            )

            agent = SceneGeneratorAgent(
                llm_service=self.llm_service,
                story=generation_input_story,
                player=player_character_schema,
                on_location_added=self._handle_location_added,
                on_character_added=self._handle_character_added,
                on_action_changed=self._handle_action_changed,
                db_session=self.db_session
            )
            self.agent = agent

            logger.info(f"Starting SceneGeneratorAgent task for story {self.story_uuid}")

            async def generation_task_wrapper():
                try:
                    characters_orm: List[CharacterOrmModel] = story_orm.characters or []
                    locations_orm: List[LocationOrmModel] = story_orm.locations or []

                    # Use the new converter utility for the list of characters
                    characters_pool_schema = convert_characters(characters_orm)
                    
                    # Use the new converter utility for the list of locations
                    locations_pool_schema = convert_locations(locations_orm)

                    previous_scene_data = None

                    assert self.agent is not None
                    final_scene_data = await self.agent.generate_scene(
                        characters=characters_pool_schema,
                        locations=locations_pool_schema,
                        previous_scene=previous_scene_data,
                    )
                    logger.info(f"Final scene data received from agent: {final_scene_data}")

                    
                    await self._send_scene_complete(final_scene_data)
                    
                    logger.info(f"Scene generation finished successfully for story {self.story_uuid}")

                except Exception as e:
                    logger.exception(f"SceneGeneratorAgent failed for story {self.story_uuid}: {e}")
                    await self._send_error(f"Scene generation failed: {str(e)}")

            self.agent_task = asyncio.create_task(generation_task_wrapper())
            await self.agent_task

        except ValueError as e:
            logger.error(f"Configuration error during scene generation setup for story {self.story_uuid}: {e}")
            await self._send_error(f"Setup error: {str(e)}")
        except Exception as e:
            logger.exception(f"Failed to start scene generation for story {self.story_uuid}: {e}")
            await self._send_error(f"Failed to start scene generation: {str(e)}")

    async def _send_update(self, message_type: str, payload: dict[str, Any]):
        """Helper to send JSON messages over the WebSocket."""
        try:
            await self.websocket.send_json({"type": message_type, "payload": payload})
        except WebSocketDisconnect:
            logger.warning(f"WebSocket disconnected while trying to send {message_type} for story {self.story_uuid}")
            await self._cleanup()
        except Exception as e:
            logger.exception(f"Failed to send {message_type} for story {self.story_uuid}: {e}")

    async def _send_location_added(self, location: LocationGenerationSchema):
        """Sends a LOCATION_ADDED message."""
        payload = location.model_dump()
        logger.info(f"Sending LOCATION_ADDED update for story {self.story_uuid}: {payload}")
        await self._send_update("LOCATION_ADDED", payload)

    async def _send_character_added(self, character: CharacterGenerationSchema):
        """Sends a CHARACTER_ADDED message."""
        payload = character.model_dump()
        logger.info(f"Sending CHARACTER_ADDED update for story {self.story_uuid}: {payload}")
        await self._send_update("CHARACTER_ADDED", payload)
        
    async def _send_action_changed(self, action_type: str, action_message: Optional[str]):
        """
        Sends an ACTION_CHANGED message with the current agent actions.
        
        Args:
            action_type: Type of action that changed
            action_message: Message describing the action, or None if action was removed
        """
        # Update our local tracking of active actions
        if action_message is None:
            # Remove the action if message is None
            if action_type in self.active_actions:
                del self.active_actions[action_type]
        else:
            # Add or update action
            self.active_actions[action_type] = action_message
            
        # Send the full set of active actions
        payload = {
            "storyId": str(self.story_uuid),
            "actions": self.active_actions
        }
        logger.info(f"Sending ACTION_CHANGED update for story {self.story_uuid}, active actions: {self.active_actions}")
        await self._send_update("ACTION_CHANGED", payload)

    async def _send_scene_complete(self, scene: SceneGenerationResult):
        """Sends the SCENE_COMPLETE message with the final scene details."""
        payload = {
            "storyId": str(self.story_uuid),
            "message": "Scene generation complete.",
            "description": scene.description,
        }
        await self._send_update("SCENE_COMPLETE", payload)

    async def _send_error(self, message: str):
        """Sends an ERROR message."""
        await self._send_update("ERROR", {"message": message})

    async def _cleanup(self):
        """Cancels any running agent task."""
        if self.agent_task and not self.agent_task.done():
            logger.info(f"Cancelling SceneGeneratorAgent task for story {self.story_uuid}")
            self.agent_task.cancel()
            try:
                await self.agent_task
            except asyncio.CancelledError:
                logger.info(f"SceneGeneratorAgent task cancelled successfully for story {self.story_uuid}")
            except Exception as e:
                logger.exception(f"Error during agent task cancellation for story {self.story_uuid}: {e}")
        try:
            await self.websocket.close()
        except RuntimeError as e:
            logger.warning(f"Error closing websocket during cleanup for story {self.story_uuid}: {e}")

    # --- Callback Methods --- #
    async def _handle_location_added(self, location: LocationGenerationSchema):
        """Callback triggered by SceneGeneratorAgent when a location is added."""
        logger.debug(f"Callback _handle_location_added called for story {self.story_uuid}")
        await self._send_location_added(location)

    async def _handle_character_added(self, character: CharacterGenerationSchema):
        """Callback triggered by SceneGeneratorAgent when a character is added."""
        logger.debug(f"Callback _handle_character_added called for story {self.story_uuid}")
        await self._send_character_added(character) 
        
    async def _handle_action_changed(self, action_type: str, action_message: Optional[str]):
        """
        Callback triggered by SceneGeneratorAgent when action status changes.
        
        Args:
            action_type: Type of action (location, character, etc.)
            action_message: Message describing the action, or None if action was removed
        """
        logger.debug(f"Callback _handle_action_changed called for story {self.story_uuid}: {action_type}={action_message}")
        await self._send_action_changed(action_type, action_message) 