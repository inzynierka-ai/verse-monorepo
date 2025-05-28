import logging
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from langfuse.decorators import observe, langfuse_context # type: ignore

from app.services.platform.llm import LLMService, ModelName
from app.services.world.world_entity_service import WorldEntityService
from app.schemas.story_generation import (
    Story,
    StoryDetails,
    StoryGenerationInput,
    StoryInput
)
from app.utils.json_service import JSONService
from app.models.story import Story as StoryModel
from app.prompts.story_generation import (
    DESCRIBE_STORY_SYSTEM_PROMPT,
    DESCRIBE_STORY_USER_PROMPT,
    CREATE_STORY_DETAILS_JSON_SYSTEM_PROMPT,
    CREATE_STORY_DETAILS_JSON_USER_PROMPT,
    CREATE_STORY_INPUT_SYSTEM_PROMPT,
    CREATE_STORY_INPUT_USER_PROMPT
)
from app.services.platform.moderations import ModerationsService

class StoryGenerator:
    """
    Service for generating story description and rules.
    It now takes the full StoryGenerationInput to provide context from both
    the desired story elements and the player character draft.
    """
    def __init__(self, llm_service: Optional[LLMService] = None, db_session: Optional[Session] = None):
        self.llm_service = llm_service or LLMService()
        self.db_session = db_session
        self.moderation_service = ModerationsService(openai_client=self.llm_service.openai_client)

    @observe(name="generate_story")
    async def generate_story(self, user_id: int, story_gen_input: StoryGenerationInput) -> Story:
        """
        Generates a detailed story from user input (including story and character draft).
        """
        # Generate story description using both story and character draft from story_gen_input
        langfuse_context.update_current_trace(input=story_gen_input)

        violated_categories = await self.moderation_service.process_moderation(story_gen_input.model_dump_json())
        if violated_categories:
            logging.warning(f"Violated categories: {violated_categories}")
            langfuse_context.update_current_trace(metadata={"violated_categories": violated_categories})
            langfuse_context.update_current_trace(output={"ERROR": "Violated categories"})
            raise ValueError(f"Sorry, we can't generate your story because it contains content that is not allowed. Please try again with different description. Reason: {', '.join(violated_categories.keys())}")

        description = await self._generate_story_description(story_gen_input)
        
        # Generate story details (title, brief description, rules) using the generated description
        # and the original story_gen_input for context.
        story_details = await self._generate_story_details(description, story_gen_input)
        
        # Generate UUID
        story_uuid = str(uuid.uuid4())
        
        # Construct story object with all required fields
        story_data = Story(
            user_id=user_id,
            title=story_details.title,
            description=description,
            brief_description=story_details.brief_description,
            rules=story_details.rules,
            uuid=story_uuid,
        )
        
        # Save to database if session is available
        if self.db_session:
            db_story = self._save_story_to_db(story_data)
            if db_story:
                # Update with database ID
                story_data.id = db_story.id # type: ignore

                # Extract and save world entities
                await self.extract_story_entities(story_data)
        
        # Always return a Story object with all required fields
        return story_data

    def _save_story_to_db(self, story: Story) -> StoryModel:
        """
        Save the generated story to the database.
        
        Args:
            story: The generated Story object
            
        Returns:
            The saved Story object with its ID
        """
        try:
            db_story = StoryModel(
                user_id=story.user_id,
                title=story.title,
                description=story.description,
                brief_description=story.brief_description,
                rules=", ".join(story.rules),
                uuid=story.uuid
            )
            
            if self.db_session is None:
                logging.warning("No database session available, story not saved")
                raise ValueError("No database session available, story not saved")
            self.db_session.add(db_story)
            self.db_session.commit()
            logging.info(f"Story {story.title} saved to database with ID {db_story.id}")
            return db_story
            
        except Exception as e:
            logging.exception(f"Failed to save story to database: {str(e)}")
            if self.db_session is not None and hasattr(self.db_session, 'is_active') and self.db_session.is_active:
                self.db_session.rollback()
            raise ValueError("Failed to save story to database")

    @observe(name="generate_story_description")
    async def _generate_story_description(self, story_gen_input: StoryGenerationInput) -> str:
        """
        Generate a detailed description of the story using story and character inputs.
        
        Args:
            story_gen_input: The full story generation input, including story parameters
                             and player character draft.
            
        Returns:
            Detailed story description as a string.
        """
        system_prompt_content = DESCRIBE_STORY_SYSTEM_PROMPT.format(
            theme=story_gen_input.story.theme,
            genre=story_gen_input.story.genre,
            year=story_gen_input.story.year,
            setting=story_gen_input.story.setting,
            character_name=story_gen_input.playerCharacter.name,
            character_age=story_gen_input.playerCharacter.age,
            character_appearance=story_gen_input.playerCharacter.appearance,
            character_background=story_gen_input.playerCharacter.background
        )
        
        messages = [
            self.llm_service.create_message("system", system_prompt_content),
            self.llm_service.create_message("user", DESCRIBE_STORY_USER_PROMPT) 
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GPT41,
            temperature=0.9,
            stream=False
        )
        
        return await self.llm_service.extract_content(response)
    
    @observe(name="extract_story_entities")
    async def extract_story_entities(self, story: Story) -> List[int]:
        """
        Extract world entities from a generated story description.
        
        Args:
            story: The generated Story object
            
        Returns:
            List of IDs of saved entities
        """
        if not self.db_session or not story.id:
            logging.warning("Cannot extract entities: missing DB session or story ID")
            return []
        
        try:
            # Create an instance of WorldEntityService
            world_entity_service = WorldEntityService(
                llm_service=self.llm_service,
                db_session=self.db_session,
                story_id=story.id
            )
            
            # Process the story description for entities
            entity_ids = await world_entity_service.process_text_for_entities(
                text=story.description,
                story_id=story.id,
                source_uuid=story.uuid  # Use story UUID as source
            )
            
            logging.info(f"Extracted {len(entity_ids)} world entities from story {story.title}")
            return entity_ids
        
        except Exception as e:
            logging.error(f"Failed to extract world entities from story: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return []
    
    @observe(name="generate_story_details")
    async def _generate_story_details(self, description: str, story_gen_input: StoryGenerationInput) -> StoryDetails:
        """
        Generate title, brief description, and rules for the story based on its description
        and original input parameters.
        
        Args:
            description: The detailed story description generated previously.
            story_gen_input: The full story generation input for context.
            
        Returns:
            StoryDetails object containing title, brief description, and rules.
        """
        system_prompt_content = CREATE_STORY_DETAILS_JSON_SYSTEM_PROMPT.format(
            theme=story_gen_input.story.theme,
            genre=story_gen_input.story.genre,
            year=story_gen_input.story.year,
            setting=story_gen_input.story.setting,
            character_name=story_gen_input.playerCharacter.name,
            character_age=story_gen_input.playerCharacter.age,
            character_appearance=story_gen_input.playerCharacter.appearance,
            character_background=story_gen_input.playerCharacter.background,
            generated_story_description=description
        )
        
        messages = [
            self.llm_service.create_message("system", system_prompt_content),
            self.llm_service.create_message("user", CREATE_STORY_DETAILS_JSON_USER_PROMPT)
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_25_FLASH_LITE,
            temperature=0.3,
            stream=False
        )
        
        content = await self.llm_service.extract_content(response)
        
        # Parse and validate the response
        story_details = JSONService.parse_and_validate_json_response(content, StoryDetails)
        return story_details

    @observe(name="create_story_input_from_description")
    async def create_story_input_from_description(self, description: str) -> StoryInput:
        """
        Create a StoryInput object from a text description.
        
        Args:
            description: A string description of a story world or concept
            
        Returns:
            A StoryInput object with theme, genre, year, and setting extracted from the description
        """
        user_prompt = CREATE_STORY_INPUT_USER_PROMPT.format(
            description=description
        )
        
        messages = [
            self.llm_service.create_message("system", CREATE_STORY_INPUT_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_25_FLASH_LITE,
            temperature=0.3,
            stream=False
        )
        
        response_text = await self.llm_service.extract_content(response)
        
        # Parse the JSON response into a StoryInput object
        story_input = JSONService.parse_and_validate_json_response(
            response_text, StoryInput)
            
        if not story_input:
            raise ValueError("No story input data found in response")
            
        return story_input