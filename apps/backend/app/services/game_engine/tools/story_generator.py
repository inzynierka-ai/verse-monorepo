from typing import Optional, List
from app.services.llm import LLMService, ModelName
from app.schemas.story_generation import (
    Story,
    StoryInput
)
from app.utils.json_service import JSONService


class StoryGenerator:
    """
    Service for generating story description and rules.
    """
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
    
    async def generate_story(self, story_input: StoryInput) -> Story:
        """
        Generates a detailed story from user input.
        
        Args:
            story_input: Basic story parameters provided by user
            
        Returns:
            A fully detailed Story object with description and rules
        """
        # Generate story description
        print("Generating story description", story_input)
        description = await self._generate_story_description(story_input)
        
        # Generate story rules
        rules = await self._generate_story_rules(description)
    
        
        # Construct and return Story object
        return Story(
            description=description,
            rules=rules,
        )
    
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
            self.llm_service.create_message("system", "You are an expert storybuilder for interactive fiction. Create detailed, immersive storys that are internally consistent and rich with storytelling potential."),
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