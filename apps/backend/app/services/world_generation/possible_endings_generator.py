from typing import Dict, Any, List, Optional

from app.services.llm import LLMService, ModelName

class PossibleEndingsGenerator:
    """
    Generator for creating multiple potential endings for the story
    based on chapter events and character relationships.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize the PossibleEndingsGenerator.
        
        Args:
            llm_service: Optional LLMService instance to use
        """
        self.llm_service = llm_service or LLMService()
    
    async def generate_endings(self, chapter_overview: str, characters: List[Dict[str, Any]], 
                              locations: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate multiple possible endings based on chapter information.
        
        Args:
            chapter_overview: Free-form overview of the chapter
            characters: List of character information
            locations: List of location information
            
        Returns:
            List of dictionaries with 'trigger' and 'result' for each ending
        """
        # Create a prompt for the LLM to generate possible endings
        prompt = self._create_endings_prompt(chapter_overview, characters, locations)
        
        # Call the LLM to generate endings
        raw_endings = await self._generate_raw_endings(prompt)
        
        # Process and structure the endings
        structured_endings = self._process_endings(raw_endings)
        
        return structured_endings
    
    def _create_endings_prompt(self, chapter_overview: str, characters: List[Dict[str, Any]], 
                              locations: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for the LLM to generate possible endings.
        
        Args:
            chapter_overview: Free-form overview of the chapter
            characters: List of character information
            locations: List of location information
            
        Returns:
            Formatted prompt string
        """
        # Extract key character information
        character_info = "\n".join([
            f"- {char.get('name', 'Unknown')}: {char.get('role', 'Unknown')} - {char.get('description', 'No description')[:100]}..."
            for char in characters[:5]  # Limit to 5 characters for prompt clarity
        ])
        
        # Extract key location information
        location_info = "\n".join([
            f"- {loc.get('name', 'Unknown')}: {loc.get('description', 'No description')[:100]}..."
            for loc in locations[:5]  # Limit to 5 locations for prompt clarity
        ])
        
        # Construct the prompt
        return f"""Based on the following chapter overview, characters, and locations, generate 4-6 possible endings to the story.
        
CHAPTER OVERVIEW:
{chapter_overview}

KEY CHARACTERS:
{character_info}

KEY LOCATIONS:
{location_info}

For each ending, include:
1. A specific trigger or decision point that leads to this ending
2. A detailed description of the resulting outcome

Return your response in this format:
Ending 1:
Trigger: [What causes this ending]
Result: [Detailed description of what happens]

Ending 2:
Trigger: [What causes this ending]
Result: [Detailed description of what happens]

And so on...
"""
    
    async def _generate_raw_endings(self, prompt: str) -> str:
        """
        Call the LLM to generate raw endings text.
        
        Args:
            prompt: The formatted prompt for ending generation
            
        Returns:
            Raw text response from the LLM
        """
        messages = [
            self.llm_service.create_message("system", 
                "You are a creative story generator specialized in creating diverse and interesting endings based on story elements."),
            self.llm_service.create_message("user", prompt)
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_PRO,  # Adjust model as needed
            temperature=0.8,  # Higher temperature for creative variety
            stream=False
        )
        
        return response
    
    def _process_endings(self, raw_endings: str) -> List[Dict[str, str]]:
        """
        Process raw LLM output into structured endings.
        
        Args:
            raw_endings: Raw text from the LLM
            
        Returns:
            List of dictionaries with 'trigger' and 'result' for each ending
        """
        # Initialize results list
        structured_endings = []
        
        # Define pattern to extract endings
        # Looking for patterns like "Ending N:" followed by "Trigger:" and "Result:" sections
        # This is a simple parser and might need refinement based on actual LLM output
        current_ending = None
        current_section = None
        
        for line in raw_endings.split('\n'):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for new ending
            if line.lower().startswith('ending'):
                # If we were processing an ending, add it to results
                if current_ending and 'trigger' in current_ending and 'result' in current_ending:
                    structured_endings.append(current_ending)
                
                # Start new ending
                current_ending = {'trigger': '', 'result': ''}
                current_section = None
                continue
            
            # Check for trigger section
            if line.lower().startswith('trigger:'):
                current_section = 'trigger'
                current_ending['trigger'] = line[len('trigger:'):].strip()
                continue
            
            # Check for result section
            if line.lower().startswith('result:'):
                current_section = 'result'
                current_ending['result'] = line[len('result:'):].strip()
                continue
            
            # Append to current section if we're in one
            if current_section and current_ending:
                current_ending[current_section] += ' ' + line
        
        # Don't forget to add the last ending
        if current_ending and 'trigger' in current_ending and 'result' in current_ending:
            structured_endings.append(current_ending)
        
        return structured_endings


async def generate_possible_endings(
    chapter_overview: str, 
    characters: List[Dict[str, Any]], 
    locations: List[Dict[str, Any]],
    llm_service: Optional[LLMService] = None
) -> Dict[str, List[Dict[str, str]]]:
    """
    Standalone function to generate possible endings.
    
    Args:
        chapter_overview: Free-form overview of the chapter
        characters: List of character information
        locations: List of location information
        llm_service: Optional LLMService instance
        
    Returns:
        Dictionary containing the possible endings
    """
    generator = PossibleEndingsGenerator(llm_service)
    possible_endings = await generator.generate_endings(chapter_overview, characters, locations)
    
    return {"possibleEndings": possible_endings} 