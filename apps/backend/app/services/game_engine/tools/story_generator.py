import logging
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session

from app.services.llm import LLMService, ModelName
from app.schemas.story_generation import (
    Story,
    StoryInput,
    StoryDetails
)
from app.utils.json_service import JSONService
from app.models.story import Story as StoryModel

class StoryGenerator:
    """
    Service for generating story description and rules.
    """
    def __init__(self, llm_service: Optional[LLMService] = None, db_session: Optional[Session] = None):
        self.llm_service = llm_service or LLMService()
        self.db_session = db_session

    async def generate_story(self, user_id: int, story_input: StoryInput) -> Story:
        """
        Generates a detailed story from user input.
        """
        # Generate story description
        description = await self._generate_story_description(story_input)
        
        # Generate story details (title, brief description, rules)
        story_details = await self._generate_story_details(description, story_input)
        
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
                story_data.id = db_story.id
        
        # Always return a Story object with all required fields
        return story_data
    def _save_story_to_db(self, story: Story) -> StoryModel:
        """
        Save the generated story to the database.
        
        Args:
            story: The generated Story object
            story_input: Basic story parameters provided by user
            
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

    async def _generate_story_description(self, story_input: StoryInput) -> str:
        """
        Generate a detailed description of the story.
        
        Args:
            story_input: Basic story input from user
            
        Returns:
            Detailed story description
        """
        prompt = f"""
        Create a detailed and immersive description of a story with the following parameters:
        
        Theme: {story_input.theme}
        Genre: {story_input.genre}
        Year: {story_input.year}
        Setting: {story_input.setting}
        
        Provide a comprehensive but concise description (300-400 words) that covers:
        - The physical environment and geography
        - Social structure and power dynamics
        - Technology level and key innovations
        - Major conflicts or tensions
        - Unique cultural elements
        
        Focus on creating a cohesive, believable story that would serve as an engaging backdrop for interactive storytelling.
        """
        
        messages = [
            self.llm_service.create_message("system", "You are an expert storybuilder for interactive fiction. Create detailed, immersive stories that are internally consistent and rich with storytelling potential."),
            self.llm_service.create_message("user", prompt)
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GPT41_MINI,
            temperature=0.7,
            stream=False
        )
        
        return await self.llm_service.extract_content(response)
    
    async def _generate_story_details(self, description: str, story_input: StoryInput) -> StoryDetails:
        """
        Generate title, brief description, and rules for the story.
        
        Args:
            description: The detailed story description
            story_input: The original story input parameters
            
        Returns:
            StoryDetails object containing title, brief description and rules
        """
        prompt = f"""
        Based on the story description below and the original parameters (Theme: {story_input.theme}, Genre: {story_input.genre}, Year: {story_input.year}, Setting: {story_input.setting}), create:

        1. A catchy, engaging title (max 50 characters)
        2. A brief summary of the story (3-4 sentences)
        3. A list of 3-5 key rules or principles that govern how this world functions
        
        Format your response as valid JSON with the following structure:
        {{
            "title": "Your Engaging Title",
            "brief_description": "Your 3-4 sentence summary...",
            "rules": [
                "Rule 1 explained in 1-2 sentences",
                "Rule 2 explained in 1-2 sentences",
                etc.
            ]
        }}

        Story description:
        {description}
        """
        
        messages = [
            self.llm_service.create_message("system", "You are an expert storybuilder creating concise, engaging story elements for interactive fiction."),
            self.llm_service.create_message("user", prompt)
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_FLASH_LITE,
            temperature=0.5,
            stream=False
        )
        
        content = await self.llm_service.extract_content(response)
        
        # Parse and validate the response
        story_details = JSONService.parse_and_validate_json_response(content, StoryDetails)
        return story_details