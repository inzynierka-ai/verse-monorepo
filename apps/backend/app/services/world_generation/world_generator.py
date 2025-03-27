from typing import Optional, List
from app.services.llm import LLMService, ModelName
from app.schemas.world_generation import (
    World,
    WorldInput
)
from app.utils.json_service import JSONService


class WorldGenerator:
    """
    Service for generating world descriptions, rules, and prologs.
    """
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
    
    async def generate_world(self, world_input: WorldInput) -> World:
        """
        Generates a detailed world from user input.
        
        Args:
            world_input: Basic world parameters provided by user
            
        Returns:
            A fully detailed World object with description, rules, and prolog
        """
        # Generate world description
        description = await self._generate_world_description(world_input)
        
        # Generate world rules
        rules = await self._generate_world_rules(description)
    
        
        # Construct and return World object
        return World(
            description=description,
            rules=rules,
        )
    
    async def _generate_world_description(self, world_input: WorldInput) -> str:
        """
        Generate a detailed description of the world.
        
        Args:
            world_input: Basic world input from user
            
        Returns:
            Detailed world description
        """
        prompt = f"""
        Create a detailed and immersive description of a world with the following parameters:
        
        Theme: {world_input.theme}
        Genre: {world_input.genre}
        Year: {world_input.year}
        Setting: {world_input.setting}
        
        Provide a comprehensive description that covers:
        - The physical environment and geography
        - Social structure and power dynamics
        - Technology level and key innovations
        - Major conflicts or tensions
        - Unique cultural elements
        
        Focus on creating a cohesive, believable world that would serve as an engaging backdrop for interactive storytelling.
        """
        
        messages = [
            self.llm_service.create_message("system", "You are an expert worldbuilder for interactive fiction. Create detailed, immersive worlds that are internally consistent and rich with storytelling potential."),
            self.llm_service.create_message("user", prompt)
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_25_PRO,
            temperature=0.7,
            stream=False
        )
        
        return await self.llm_service.extract_content(response)
    
    async def _generate_world_rules(self, description: str) -> List[str]:
        """
        Generate a list of rules that govern the world.
        
        Args:
            description: The detailed world description
            
        Returns:
            List of world rules
        """
        prompt = f"""
        Based on this world description:
        
        {description}
        
        Create a list of 5-8 key rules or principles that govern how this world functions. These should include:
        
        - Physical laws (if different from our world)
        - Social norms and taboos
        - Economic principles
        - Power structures
        - Any supernatural or technological constraints
        
        Format your response as a JSON array of objects, where each object has a "rule" property containing 
        a distinct rule explained in 1-2 sentences.
        
        Example format:
        [
            "Gravity is 1.5 times Earth normal, making physical activities more strenuous and affecting architecture.",
            "Mind-reading is possible but strictly regulated by the governing council."
        ]
        """
        
        messages = [
            self.llm_service.create_message("system", "You are an expert worldbuilder specializing in creating consistent rule systems for fictional worlds. Create logical, coherent rules that define how the world functions. Always respond with valid JSON."),
            self.llm_service.create_message("user", prompt)
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