from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.services.llm import LLMService
from app.schemas.world_wizard import WorldSettings, WorldRule

class WorldSetting(BaseModel):
    description: str
    rules: List[WorldRule]
    backstory: str

class WorldTemplate(BaseModel):
    setting: WorldSetting
    basic_characters: List[Dict[str, Any]]
    basic_locations: List[Dict[str, Any]]

class WorldGenerator:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def create_world_template(self, settings: WorldSettings) -> WorldTemplate:
        """
        Generate high-level overview of the world and transform it into structured data
        
        Args:
            settings: User-provided settings for world generation
            
        Returns:
            WorldTemplate with setting, basic character and location information
        """
        # Generate the high-level free text overview of the world
        world_overview_prompt = self._build_world_overview_prompt(settings)
        world_overview_response = await self.llm_service.generate_text(world_overview_prompt)
        
        # Transform the free text into structured JSON
        structured_world_prompt = self._build_structured_world_prompt(settings, world_overview_response)
        structured_world_json = await self.llm_service.generate_json(structured_world_prompt)
        
        # Extract and format the data
        world_data = structured_world_json.get("world", {})
        
        # Create WorldRule objects for each rule
        world_rules = []
        for rule_data in world_data.get("rules", []):
            # Handle both string rules and dictionary rules with name/description
            if isinstance(rule_data, str):
                # For simple string rules, use the string as the description
                world_rules.append(WorldRule(name=f"Rule", description=rule_data))
            elif isinstance(rule_data, dict) and "description" in rule_data:
                # For dictionary rules with a description
                name = rule_data.get("name", "Rule")
                world_rules.append(WorldRule(name=name, description=rule_data["description"]))
        
        # Create the setting model
        setting = WorldSetting(
            description=world_data.get("description", ""),
            rules=world_rules,
            backstory=world_data.get("prolog", "")
        )
        
        # Extract basic character and location information
        basic_characters = structured_world_json.get("basicCharacters", [])
        basic_locations = structured_world_json.get("basicLocations", [])
        
        return WorldTemplate(
            setting=setting,
            basic_characters=basic_characters,
            basic_locations=basic_locations
        )
    
    def _build_world_overview_prompt(self, settings: WorldSettings) -> str:
        """Build prompt for generating free-form world overview"""
        prompt = f"""
        Create a detailed description of an imaginative world based on the following parameters:
        
        {settings.description}
        
        {settings.additional_context if settings.additional_context else ""}
        
        Your response should include:
        1. A vivid description of the world setting, atmosphere, and key features
        2. Important rules or principles that govern this world
        3. A backstory or prolog that explains how this world came to be
        
        Be creative and detailed while maintaining consistency with the provided parameters.
        """
        return prompt
    
    def _build_structured_world_prompt(self, settings: WorldSettings, world_overview: str) -> str:
        """Build prompt for transforming free text into structured JSON"""
        prompt = f"""
        Based on the following world description:
        
        {world_overview}
        
        And these input parameters:
        {settings.description}
        {settings.additional_context if settings.additional_context else ""}
        
        Transform this description into a structured JSON format with the following components:
        
        1. "world": An object containing:
           - "description": A concise description of the world
           - "rules": An array of objects, each with a "name" and "description" field representing a rule or principle of the world
           - "prolog": A backstory explaining the world's origin
        
        2. "basicCharacters": An array of character outlines that would exist in this world,
           with each character having at least an "id", "name", and brief "description"
           
           If a player character was specified in the input, make sure to include them
           as one of the characters with appropriate connections to the world.
        
        3. "basicLocations": An array of location outlines in this world,
           with each location having at least an "id", "name", and brief "description"
        
        Return only valid JSON with these components.
        """
        return prompt 