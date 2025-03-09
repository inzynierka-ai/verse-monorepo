from typing import  Optional
import json
from app.services.llm import LLMService, ModelName
from app.schemas.world_wizard import (
    WorldTemplate,
    WorldSettings,
)
from app.prompts import (
    WORLD_WIZARD_SYSTEM_PROMPT,
    WORLD_STRUCTURE_SYSTEM_PROMPT,
    WORLD_WIZARD_USER_PROMPT_TEMPLATE,
    WORLD_STRUCTURE_USER_PROMPT_TEMPLATE,
)


class WorldWizard:
    """
    World Wizard module for generating game worlds.
    Provides tools for describing worlds and creating structured JSON representations.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize the World Wizard agent.
        
        Args:
            llm_service: LLMService instance to use for generating completions
        """
        self.llm_service = llm_service or LLMService()
    
    async def describe_world(self, settings: WorldSettings) -> str:
        """
        Generate a narrative description of a world based on the provided settings.
        
        Args:
            settings: Settings containing description and optional parameters
            
        Returns:
            A detailed narrative description of the world
        """
        if not settings.description:
            raise ValueError("Description is required for world generation")
            
        # Format the user prompt with the description
        user_prompt = WORLD_WIZARD_USER_PROMPT_TEMPLATE.format(
            description=settings.description,
            additional_context=settings.additional_context or ""
        )
        
        # Call the LLM and return the response
        messages = [
            self.llm_service.create_message("system", WORLD_WIZARD_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]
        
        return await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_PRO,
            temperature=0.7,
            stream=False
        )
    
    async def create_world_template(self, settings: WorldSettings) -> WorldTemplate:
        """
        Generate a structured world template based on the provided settings.
        
        Args:
            settings: Settings containing description and optional parameters
            
        Returns:
            A structured WorldTemplate object
        """
        if not settings.description:
            raise ValueError("Description is required for world template generation")
            
        # Generate an expanded description if needed
        expanded_description = await self.describe_world(settings)
            
        # Format the user prompt with the description
        user_prompt = WORLD_STRUCTURE_USER_PROMPT_TEMPLATE.format(
            world_description=expanded_description
        )
        
        # Call the LLM to generate a structured world template
        messages = [
            self.llm_service.create_message("system", WORLD_STRUCTURE_SYSTEM_PROMPT),
            self.llm_service.create_message("user", user_prompt)
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_PRO,
            temperature=0.7,
            stream=False
        )

        print(response)
        
        # Parse the response into a WorldTemplate
        return self._parse_world_template(response)
        
    def _parse_world_template(self, response: str) -> WorldTemplate:
        """
        Parse the LLM response into a WorldTemplate object.
        
        Args:
            response: The LLM response text
            
        Returns:
            A WorldTemplate object
        """
        try:
            # Extract the JSON content from the response
            json_content = self._extract_json_from_response(response)
            
            # Parse the JSON content
            template_data = json.loads(json_content)
            
            # Create and return a WorldTemplate object
            return WorldTemplate.model_validate(template_data)
            
        except Exception as e:
            raise ValueError(f"Failed to parse world template: {str(e)}")
            
    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON content from a response that might contain markdown.
        
        Args:
            response: The response text
            
        Returns:
            Extracted JSON content as string
        """
        if not response:
            raise ValueError("Empty response received from LLM")
            
        if "```json" in response:
            return response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            return response.split("```")[1].split("```")[0].strip()
        else:
            return response.strip()