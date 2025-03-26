from typing import Dict, Any, Optional, Tuple, List
from openai.types.chat import ChatCompletionMessageParam

from app.services.llm import LLMService, ModelName

class ChapterGenerator:
    """
    Generator for creating chapter overviews based on the Hero's Journey framework.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize the ChapterGenerator.
        
        Args:
            llm_service: Optional LLMService instance to use
        """
        self.llm_service = llm_service or LLMService()
    
    async def generate_chapter_overview(self, world_description: Dict[str, Any], 
                                        chapter_number: int = 1) -> str:
        """
        Generate a free-form chapter overview using the Hero's Journey framework.
        
        Args:
            world_description: Dictionary containing world information
            chapter_number: The number of the chapter to generate
            
        Returns:
            Free-form chapter overview text
        """
        # Create a prompt for the LLM to generate the chapter overview
        prompt = self._create_chapter_prompt(world_description, chapter_number)
        
        # Call the LLM to generate the chapter overview
        chapter_overview = await self._generate_chapter_text(prompt)
        
        return chapter_overview
    
    def _create_chapter_prompt(self, world_description: Dict[str, Any], chapter_number: int) -> str:
        """
        Create a prompt for the LLM to generate a chapter overview.
        
        Args:
            world_description: Dictionary containing world information
            chapter_number: The number of the chapter to generate
            
        Returns:
            Formatted prompt string
        """
        # Extract relevant information from world description
        world_desc = world_description.get("world", {}).get("description", "A mysterious world")
        world_rules = world_description.get("world", {}).get("rules", ["The world follows mysterious rules"])
        
        # Determine which stage of the Hero's Journey to use based on chapter number
        journey_stage, stage_desc = self._get_heros_journey_stage(chapter_number)
        
        # Construct the prompt
        return f"""Based on the following world description, create a compelling chapter overview using the Hero's Journey framework.
        
WORLD DESCRIPTION:
{world_desc}

WORLD RULES:
- {' '.join(world_rules[:3])}

HERO'S JOURNEY STAGE: {journey_stage}
{stage_desc}

Create a rich, evocative chapter overview that fits this stage of the Hero's Journey.
Your overview should include:
1. The main situations and conflicts that will arise
2. The emotional and physical challenges the protagonist will face
3. Key decision points that could lead to different outcomes
4. The atmosphere and tone of this chapter

Provide a cohesive narrative overview of approximately 300-500 words. Focus on creating a vivid picture
that will serve as the foundation for generating characters, locations, and possible endings.
"""
    
    async def _generate_chapter_text(self, prompt: str) -> str:
        """
        Call the LLM to generate the chapter overview text.
        
        Args:
            prompt: The formatted prompt for chapter generation
            
        Returns:
            Chapter overview text from the LLM
        """
        messages: List[ChatCompletionMessageParam] = [
            self.llm_service.create_message("system", 
                "You are a master storyteller specialized in creating compelling narratives using the Hero's Journey framework."),
            self.llm_service.create_message("user", prompt)
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_25_PRO,  # Adjust model as needed
            temperature=0.7,
            stream=False
        )
        
        return response.strip() # type: ignore
    
    def _get_heros_journey_stage(self, chapter_number: int) -> Tuple[str, str]:
        """
        Get the appropriate Hero's Journey stage based on chapter number.
        
        Args:
            chapter_number: The chapter number
            
        Returns:
            Tuple of (stage_name, stage_description)
        """
        # Define the stages of the Hero's Journey
        stages = [
            ("The Ordinary World", 
             "The hero begins in a mundane situation showing their everyday life, personality, and limitations."),
            
            ("The Call to Adventure", 
             "The hero receives a call to enter an unusual world with unfamiliar rules and values."),
            
            ("Refusal of the Call", 
             "The hero is reluctant to follow the call to adventure, expressing hesitation or outright refusal."),
            
            ("Meeting with the Mentor", 
             "The hero encounters a seasoned traveler of the worlds who gives them training, equipment, or advice."),
            
            ("Crossing the Threshold", 
             "The hero commits to leaving the ordinary world and enters a new region or condition with unfamiliar rules."),
            
            ("Tests, Allies and Enemies", 
             "The hero faces tests, acquires allies, confronts enemies, and learns the rules of the special world."),
            
            ("Approach", 
             "The hero and newfound allies prepare for the major challenge of the special world."),
            
            ("The Ordeal", 
             "The hero faces their greatest fear, confronts their most difficult challenge, and faces the possibility of death."),
            
            ("Reward", 
             "The hero takes possession of the treasure won by facing death, celebrating their victory despite dangers ahead."),
            
            ("The Road Back", 
             "The hero must return to the ordinary world with the reward, facing pursuit and often a final confrontation."),
            
            ("The Resurrection", 
             "The hero is severely tested once more on the threshold of home, emerging in a form of rebirth or renaissance."),
            
            ("Return with the Elixir", 
             "The hero returns with something to improve the ordinary world, having grown or been transformed.")
        ]
        
        # Map chapter number to stage, with later chapters potentially cycling through the stages again
        index = (chapter_number - 1) % len(stages)
        return stages[index]


async def generate_chapter(
    world_description: Dict[str, Any],
    chapter_number: int = 1,
    llm_service: Optional[LLMService] = None
) -> Dict[str, str]:
    """
    Standalone function to generate a chapter overview.
    
    Args:
        world_description: Dictionary containing world information
        chapter_number: The number of the chapter to generate
        llm_service: Optional LLMService instance
        
    Returns:
        Dictionary containing the chapter overview
    """
    generator = ChapterGenerator(llm_service)
    chapter_overview = await generator.generate_chapter_overview(world_description, chapter_number)
    
    return {"chapterOverview": chapter_overview} 