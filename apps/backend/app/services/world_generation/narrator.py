import json
import re
from typing import Dict, Any, List, Optional

from app.services.llm import LLMService, ModelName

class Narrator:
    """
    Narrator module for generating immersive game introductions based on
    world generation output using LLM enhancement.
    """
    
    def __init__(self, world_data: Dict[str, Any], llm_service: Optional[LLMService] = None):
        """
        Initialize the Narrator with world data and optional LLM service.
        
        Args:
            world_data: Complete world generation output as a dictionary
            llm_service: Optional LLMService instance to use for enhanced narration
        """
        self.world_data = world_data
        self.llm_service = llm_service or LLMService()
        self.player_character = self._find_player_character()
        self.starting_location = self._find_starting_location()
        
    def _find_player_character(self) -> Dict[str, Any]:
        """Find the player character from the characters list."""
        for character in self.world_data.get("characters", []):
            if character.get("role", "").lower() == "player character":
                return character
        # Fallback to first character if no explicit player character
        return self.world_data.get("characters", [{}])[0]
    
    def _find_starting_location(self) -> Dict[str, Any]:
        """Find the starting location for the player."""
        # Try to find location connected to player character
        player_id = self.player_character.get("id", "")
        
        # Check character connections for the first location
        for conn in self.world_data.get("connections", {}).get("character_connections", []):
            if conn.get("character_id") == player_id and conn.get("connected_locations"):
                location_id = conn.get("connected_locations")[0]
                for location in self.world_data.get("locations", []):
                    if location.get("id") == location_id:
                        return location
        
        # Fallback to first location
        return self.world_data.get("locations", [{}])[0]
    
    def _format_text(self, text: str) -> str:
        """
        Format text for better readability and presentation.
        
        Args:
            text: The text to format
            
        Returns:
            Formatted text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Ensure the text ends with a period
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
            
        return text
    
    def _extract_first_sentences(self, text: str, count: int = 2) -> str:
        """
        Extract the first N sentences from a text.
        
        Args:
            text: The text to extract from
            count: Number of sentences to extract
            
        Returns:
            The extracted sentences
        """
        if not text:
            return ""
            
        # Split by sentence endings followed by a space
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Take the requested number of sentences
        selected = sentences[:count]
        
        # Join and return
        result = " ".join(selected)
        
        # Ensure it ends with proper punctuation
        if result and not result.endswith(('.', '!', '?')):
            result += '.'
            
        return result
    
    async def generate_introduction(self, use_llm: bool = True) -> List[Dict[str, str]]:
        """
        Generate a 5-step immersive introduction based on the world data.
        
        Args:
            use_llm: Whether to use LLM enhancement (defaults to True)
            
        Returns:
            A list of dictionaries with 'title' and 'content' for each step
        """
        if use_llm:
            try:
                # Use LLM for enhanced narration
                return await self._generate_llm_introduction()
            except Exception as e:
                print(f"Warning: LLM introduction generation failed: {str(e)}")
                print("Falling back to template-based introduction...")
                
        # Fallback to template-based introduction
        return [
            self._generate_setting_establishment(),
            self._generate_character_introduction(),
            self._generate_conflict_glimpse(),
            self._generate_location_focus(),
            self._generate_call_to_action()
        ]
    
    async def _generate_llm_introduction(self) -> List[Dict[str, str]]:
        """
        Generate an immersive introduction using LLM.
        
        Returns:
            A list of dictionaries with 'title' and 'content' for each step
        """
        # Prepare prompts for each step
        prompts = [
            self._prepare_setting_prompt(),
            self._prepare_character_prompt(),
            self._prepare_conflict_prompt(),
            self._prepare_location_prompt(),
            self._prepare_call_to_action_prompt()
        ]
        
        # Generate content for each step
        results = []
        for i, (title, prompt) in enumerate(prompts):
            content = await self._generate_llm_content(prompt)
            results.append({
                "title": title,
                "content": content
            })
            
        return results
    
    async def _generate_llm_content(self, prompt: str) -> str:
        """
        Generate content using LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The generated content
        """
        system_message = """You are a master storyteller creating an immersive introduction for a narrative game. 
Your task is to craft evocative, engaging prose that draws players into the world.
Write in second person perspective where appropriate.
Aim for 3-4 sentences that paint a vivid picture and establish the right tone.
Focus on sensory details, emotional resonance, and creating intrigue.
Avoid exposition dumps or overwhelming details.
Create text that would appear during a game's opening sequence."""
        
        messages = [
            self.llm_service.create_message("system", system_message),
            self.llm_service.create_message("user", prompt)
        ]
        
        response = await self.llm_service.generate_completion(
            messages=messages,
            model=ModelName.GEMINI_2_PRO,
            temperature=0.8,
            stream=False
        )
        
        # Clean up the response
        result = self._format_text(response)
        
        return result
    
    def _prepare_setting_prompt(self) -> tuple:
        """Prepare prompt for setting establishment."""
        setting_summary = self.world_data.get("setting", {}).get("summary", "")
        
        # Get relevant world rules
        world_rules = self.world_data.get("world_rules", [])
        rules_text = ""
        for rule in world_rules[:3]:  # Include up to 3 rules
            rules_text += f"- {rule.get('name', '')}: {rule.get('description', '')}\n"
        
        prompt = f"""Create an immersive introduction to the game world that establishes the setting, time period, and atmosphere.

WORLD SETTING:
{setting_summary}

WORLD RULES:
{rules_text}

Write 3-4 evocative sentences that introduce players to this world, focusing on what makes it unique, 
interesting, and atmospheric. End with a sense of tension or possibility that draws the player in.
"""
        
        return ("The World Awaits", prompt)
    
    def _prepare_character_prompt(self) -> tuple:
        """Prepare prompt for character introduction."""
        name = self.player_character.get("name", "")
        description = self.player_character.get("description", "")
        backstory = self.player_character.get("backstory", "")
        
        # Get personality traits
        traits = self.player_character.get("personality_traits", [])
        traits_text = ""
        for trait in traits[:3]:  # Include up to 3 traits
            traits_text += f"- {trait.get('name', '')}: {trait.get('description', '')}\n"
        
        # Goals
        goals = self.player_character.get("goals", [])
        goals_text = "\n".join([f"- {goal}" for goal in goals[:3]])
        
        prompt = f"""Create an introduction to the player character that makes them feel embodied in the role.

CHARACTER NAME: {name}

DESCRIPTION:
{description}

BACKSTORY:
{backstory}

PERSONALITY TRAITS:
{traits_text}

GOALS:
{goals_text}

Write 3-4 sentences in second-person perspective that introduce the player to their character,
focusing on who they are, what motivates them, and what makes them unique.
Make the player feel connected to this character.
"""
        
        return ("Your Identity", prompt)
    
    def _prepare_conflict_prompt(self) -> tuple:
        """Prepare prompt for conflict glimpse."""
        conflict = self.world_data.get("conflict", {})
        title = conflict.get("title", "")
        description = conflict.get("description", "")
        
        # Get faction information
        factions = conflict.get("factions", [])
        factions_text = ""
        for faction in factions[:2]:  # Include up to 2 factions
            factions_text += f"- {faction.get('name', '')}: {faction.get('motivation', '')}\n"
        
        # Stakes
        personal_stakes = conflict.get("personal_stakes", "")
        world_stakes = conflict.get("world_stakes", "")
        
        prompt = f"""Create a glimpse of the central conflict that will drive the narrative.

CONFLICT TITLE: {title}

DESCRIPTION:
{description}

KEY FACTIONS:
{factions_text}

PERSONAL STAKES:
{personal_stakes}

WORLD STAKES:
{world_stakes}

Write 3-4 sentences that introduce the central conflict, creating intrigue and tension.
Focus on what's at stake, the opposing forces, and why this matters to the player character.
Create a sense of urgency without revealing everything.
"""
        
        return (f"The {title or 'Challenge'}", prompt)
    
    def _prepare_location_prompt(self) -> tuple:
        """Prepare prompt for location focus."""
        name = self.starting_location.get("name", "")
        description = self.starting_location.get("description", "")
        atmosphere = self.starting_location.get("atmosphere", "")
        
        # Get interactive elements
        interactive_elements = self.starting_location.get("interactive_elements", [])
        elements_text = ""
        for element in interactive_elements[:2]:  # Include up to 2 elements
            elements_text += f"- {element.get('name', '')}: {element.get('description', '')}\n"
        
        prompt = f"""Create a vivid description of the player's starting location.

LOCATION NAME: {name}

DESCRIPTION:
{description}

ATMOSPHERE:
{atmosphere}

KEY ELEMENTS:
{elements_text}

Write 3-4 sentences that establish the player's immediate surroundings in second-person perspective.
Focus on sensory details (sights, sounds, smells, etc.) that make the location feel real and present.
Create a strong sense of place and hint at what the player might discover or interact with.
"""
        
        return ("Your Surroundings", prompt)
    
    def _prepare_call_to_action_prompt(self) -> tuple:
        """Prepare prompt for call to action."""
        # Get player goals
        goals = self.player_character.get("goals", [])
        first_goal = goals[0] if goals else "Uncover the truth"
        
        # Get story hooks
        story_hooks = self.world_data.get("story_hooks", [])
        hooks_text = ""
        for hook in story_hooks[:2]:  # Include up to 2 hooks
            hooks_text += f"- {hook.get('title', '')}: {hook.get('description', '')}\n"
        
        # Get conflict info
        conflict = self.world_data.get("conflict", {})
        possible_resolutions = conflict.get("possible_resolutions", [])
        resolutions_text = ""
        for resolution in possible_resolutions[:2]:  # Include up to 2 resolutions
            resolutions_text += f"- {resolution.get('path', '')}: {resolution.get('description', '')}\n"
        
        prompt = f"""Create a compelling call to action that sets the player on their journey.

PRIMARY GOAL: {first_goal}

POTENTIAL STORY HOOKS:
{hooks_text}

POSSIBLE PATHS:
{resolutions_text}

Write 3-4 sentences that motivate the player to begin their adventure.
Focus on their immediate objective, the sense of possibility ahead, and why their choices matter.
End with a powerful statement that propels them forward into the game world.
"""
        
        return ("Your Journey Begins", prompt)
    
    def _generate_setting_establishment(self) -> Dict[str, str]:
        """Generate the first step: Setting Establishment using templates."""
        setting_summary = self.world_data.get("setting", {}).get("summary", "")
        world_rules = self.world_data.get("world_rules", [])
        
        # Extract atmospheric elements from world rules
        atmosphere_elements = []
        for rule in world_rules:
            if "atmosphere" in rule.get("name", "").lower() or any(word in rule.get("description", "").lower() 
                                                                 for word in ["air", "feeling", "mood", "environment"]):
                atmosphere_elements.append(rule.get("description", ""))
        
        # Create content with 3-4 sentences
        content = self._format_text(setting_summary)
        
        # If the setting is too long, extract just the first 2-3 sentences
        if len(content.split()) > 80:
            content = self._extract_first_sentences(content, 3)
        
        if atmosphere_elements:
            atmos = self._extract_first_sentences(atmosphere_elements[0], 1)
            content += f" {atmos}"
            
        # Add a final sentence about the world's current state
        content += " The world stands at a crossroads, with forces in motion that will shape its destiny."
            
        return {
            "title": "The World Awaits",
            "content": content
        }
    
    def _generate_character_introduction(self) -> Dict[str, str]:
        """Generate the second step: Character Introduction using templates."""
        name = self.player_character.get("name", "")
        description = self.player_character.get("description", "")
        backstory = self.player_character.get("backstory", "")
        
        # Get 1-2 personality traits
        traits = self.player_character.get("personality_traits", [])
        trait_descriptions = []
        if traits and len(traits) > 0:
            trait_descriptions = [trait.get("description", "") for trait in traits[:2]]
        
        # Create content with 3-4 sentences
        content = f"You are {name}."
        
        # Add first 1-2 sentences of description
        if description:
            desc_intro = self._extract_first_sentences(description, 2)
            content += f" {desc_intro}"
        
        # Add one personality trait
        if trait_descriptions:
            trait = self._format_text(trait_descriptions[0])
            content += f" {trait}"
            
        # Add first sentence of backstory
        if backstory:
            backstory_intro = self._extract_first_sentences(backstory, 1)
            content += f" {backstory_intro}"
        
        return {
            "title": "Your Identity",
            "content": content
        }
    
    def _generate_conflict_glimpse(self) -> Dict[str, str]:
        """Generate the third step: Conflict Glimpse using templates."""
        conflict = self.world_data.get("conflict", {})
        title = conflict.get("title", "")
        description = conflict.get("description", "")
        
        # Try to find the first sentence or a short excerpt
        first_sentence = ""
        if description:
            first_sentence = self._extract_first_sentences(description, 1)
        else:
            first_sentence = "A conflict brews in the shadows, its true nature yet to be revealed."
        
        # Get faction info
        factions = conflict.get("factions", [])
        faction_info = ""
        if factions and len(factions) > 0:
            faction = factions[0]
            name = faction.get('name', 'unknown forces')
            methods = self._extract_first_sentences(faction.get('methods', ''), 1)
            if methods:
                faction_info = f"The {name} {methods}"
        
        # Add stakes
        personal_stakes = conflict.get("personal_stakes", "")
        
        # Create content with 3-4 sentences
        content = first_sentence
        
        if faction_info:
            content += f" {faction_info}"
            
        if personal_stakes:
            stakes = self._extract_first_sentences(personal_stakes, 1)
            content += f" {stakes}"
        else:
            content += " The consequences of failure are dire, both for you and for everyone around you."
            
        # Add a final sentence about the conflict's immediacy
        content += " Time is not on your side, and decisions must be made soon."
        
        # Final formatting
        content = self._format_text(content)
        
        return {
            "title": f"The {title or 'Challenge'}",
            "content": content
        }
    
    def _generate_location_focus(self) -> Dict[str, str]:
        """Generate the fourth step: Location Focus using templates."""
        name = self.starting_location.get("name", "")
        description = self.starting_location.get("description", "")
        
        # Extract interactive elements
        interactive_elements = self.starting_location.get("interactive_elements", [])
        element_desc = ""
        if interactive_elements and len(interactive_elements) > 0:
            element = interactive_elements[0]
            element_name = element.get('name', '')
            element_description = element.get('description', '')
            if element_name and element_description:
                element_desc = f"A {element_name.lower()} {element_description.lower()}."
        
        # Get atmosphere if available
        atmosphere = self.starting_location.get("atmosphere", "")
        
        # Create content with 3-4 sentences
        content = f"You find yourself in {name}."
        
        if description:
            # Extract only 1-2 sentences of the description to keep it concise
            desc_excerpt = self._extract_first_sentences(description, 2)
            content += f" {desc_excerpt}"
            
        if element_desc:
            content += f" {element_desc}"
            
        if atmosphere:
            # Extract first sentence of atmosphere
            atmos_sentence = self._extract_first_sentences(atmosphere, 1)
            content += f" {atmos_sentence}"
            
        # Final formatting
        content = self._format_text(content)
            
        return {
            "title": "Your Surroundings",
            "content": content
        }
    
    def _generate_call_to_action(self) -> Dict[str, str]:
        """Generate the fifth step: Call to Action using templates."""
        # Get player goals
        goals = self.player_character.get("goals", [])
        first_goal = goals[0] if goals else "Uncover the truth"
        
        # Get story hooks for potential directions
        story_hooks = self.world_data.get("story_hooks", [])
        hook_direction = ""
        if story_hooks and len(story_hooks) > 0:
            hook = story_hooks[0]
            hook_description = hook.get('description', '')
            if hook_description:
                hook_direction = self._extract_first_sentences(hook_description, 1)
        
        # Get world stakes
        world_stakes = self.world_data.get("conflict", {}).get("world_stakes", "")
        
        # Create content with 3-4 sentences
        content = f"Your journey begins with a clear purpose: {first_goal}."
        
        if hook_direction:
            content += f" {hook_direction}"
            
        if world_stakes:
            stakes = self._extract_first_sentences(world_stakes, 1)
            content += f" {stakes}"
        else:
            content += " The fate of this world may well rest on your shoulders."
            
        # Final call to action
        content += " The path forward is uncertain, but you must take the first step."
        
        # Final formatting
        content = self._format_text(content)
        
        return {
            "title": "Your Journey Begins",
            "content": content
        }
    
    @staticmethod
    async def from_json_file(file_path: str, llm_service: Optional[LLMService] = None) -> 'Narrator':
        """
        Create a Narrator instance from a JSON file.
        
        Args:
            file_path: Path to the JSON file with world data
            llm_service: Optional LLMService instance
            
        Returns:
            Initialized Narrator instance
        """
        with open(file_path, 'r') as f:
            world_data = json.load(f)
        return Narrator(world_data, llm_service)
    
    @staticmethod
    async def from_json_string(json_string: str, llm_service: Optional[LLMService] = None) -> 'Narrator':
        """
        Create a Narrator instance from a JSON string.
        
        Args:
            json_string: JSON string with world data
            llm_service: Optional LLMService instance
            
        Returns:
            Initialized Narrator instance
        """
        world_data = json.loads(json_string)
        return Narrator(world_data, llm_service)


async def generate_introduction(world_data: Dict[str, Any], 
                              llm_service: Optional[LLMService] = None, 
                              use_llm: bool = True) -> List[Dict[str, str]]:
    """
    Helper function to generate a 5-step introduction from world data.
    
    Args:
        world_data: World generation output as a dictionary
        llm_service: Optional LLMService instance
        use_llm: Whether to use LLM enhancement
        
    Returns:
        A list of dictionaries with 'title' and 'content' for each step
    """
    narrator = Narrator(world_data, llm_service)
    return await narrator.generate_introduction(use_llm) 