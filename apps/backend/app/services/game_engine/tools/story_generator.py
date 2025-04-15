import logging
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session

from app.services.llm import LLMService, ModelName
from app.schemas.story_generation import (
    Story,
    StoryInput
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
        
        # Generate story rules
        rules = await self._generate_story_rules(description)

        # Create title from input
        title = f"{story_input.theme}, {story_input.genre}, {story_input.year}"
        
        # Generate UUID
        story_uuid = str(uuid.uuid4())
        
        # Construct story object with all required fields
        story_data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "rules": rules,
            "uuid": story_uuid,
            "id": None  # Default value
        }
        
        # Save to database if session is available
        if self.db_session:
            db_story = self._save_story_to_db(Story(**story_data))
            if db_story:
                # Update with database ID
                story_data["id"] = db_story.id
        
        # Always return a Story object with all required fields
        return Story(**story_data)
    
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
                rules=", ".join(story.rules),
                uuid=story.uuid
            )
            
            if self.db_session is None:
                logging.warning("No database session available, story not saved")
                return None
            self.db_session.add(db_story)
            self.db_session.commit()
            logging.info(f"Story {story.title} saved to database with ID {db_story.id}")
            return db_story
            
        except Exception as e:
            logging.exception(f"Failed to save story to database: {str(e)}")
            if self.db_session is not None and hasattr(self.db_session, 'is_active') and self.db_session.is_active:
                self.db_session.rollback()
            return None

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
        
        Provide a comprehensive description that covers:
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
            model=ModelName.GPT4O_MINI,
            temperature=0.7,
            stream=False
        )
        
        return await self.llm_service.extract_content(response)
    
    async def _generate_story_rules(self, description: str) -> List[str]:
        """
        Generate a list of rules that govern the story.
        
        Args:
            description: The detailed story description
            
        Returns:
            List of story rules
        """
        prompt = """
        Based on the story description create a list of 5-8 key rules or principles that govern how this story functions. These should include:
        
        - Physical laws (if different from our story)
        - Social norms and taboos
        - Economic principles
        - Power structures
        - Any supernatural or technological constraints
        
        Format your response as a JSON array of strings, where each string contains a distinct rule explained in 1-2 sentences.
        
        Example format:
        [
            "Gravity is 1.5 times Earth normal, making physical activities more strenuous and affecting architecture.",
            "Mind-reading is possible but strictly regulated by the governing council."
        ]
        """
        
        messages = [
            self.llm_service.create_message("system", prompt),
            self.llm_service.create_message("user", description)
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_FLASH_LITE,
            temperature=0.5,
            stream=False
        )
        
        content = await self.llm_service.extract_content(response)
        
        rule_items = JSONService.parse_and_validate_string_list(content)
        return rule_items