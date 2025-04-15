import json
from typing import List, Dict, Any, Optional
import logging

from app.services.llm import LLMService, ModelName
from app.schemas.scene_generator import SceneGeneratorState
from app.schemas.character import Character
from app.schemas.location import Location
from app.services.game_engine.tools.location_generator import LocationGenerator
from app.services.game_engine.tools.character_generator import CharacterGenerator
from app.schemas.story_generation import Story

class SceneGeneratorAgent:
    """Agent that generates scenes for the narrative adventure game"""
    
    def __init__(self, llm_service: LLMService, story: Story, player: Character):
        """
        Initialize the scene generator agent.
        
        Args:
            llm_service: LLM service for generating text
            story: Story object containing details about the game world
            player: Player character
        """
        self.llm = llm_service
        self.story = story
        self.player = player
        self.location_generator = LocationGenerator(llm_service)
        self.character_generator = CharacterGenerator(llm_service)
        self.tools = self._register_tools()
        
        # Initialize with empty state
        self.state = SceneGeneratorState(
            story=story,
            player=player,
            characters_pool=[],
            locations_pool=[],
            selected_characters=[]
        )
        
    def _register_tools(self) -> List[Dict[str, Any]]:
        """Register tools for the agent to use during scene generation"""
        
        location_generator = LLMService.create_tool({
            "name": "generate_location",
            "description": "Generate a new location or select an existing one for the scene",
            "parameters": {
                "type": "object",
                "properties": {
                    "brief_description": {
                        "type": "string", 
                        "description": "Brief description to guide location generation"
                    },
                    "existing_location_id": {
                        "type": "string", 
                        "description": "UUID of existing location to use (optional)"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Explain why this location was chosen for the scene"
                    }
                },
                "required": ["brief_description", "reasoning"]
            }
        })
        
        character_generator = LLMService.create_tool({
            "name": "generate_character",
            "description": "Generate a new character or select existing ones for the scene (up to 3)",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_draft": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer"},
                            "appearance": {"type": "string"},
                            "background": {"type": "string"}
                        },
                        "required": ["name", "age", "appearance", "background"]
                    },
                    "existing_character_id": {
                        "type": "string",
                        "description": "UUID of existing character to use (optional)"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Explain why this character was chosen for the scene"
                    }
                },
                "required": ["reasoning"]
            }
        })
        
        finalize_scene = LLMService.create_tool({
            "name": "finalize_scene",
            "description": "Complete the scene with selected characters and location",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string", 
                        "description": "Compelling scene description to display to the user"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Explain your thought process for this scene"
                    }
                },
                "required": ["description", "reasoning"]
            }
        })
        
        return [location_generator, character_generator, finalize_scene]
        
    async def generate_scene(
        self, 
        characters: List[Character], 
        locations: List[Location], 
        previous_scene: Optional[Dict[str, Any]] = None,
        relevant_conversations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a new scene for the game
        
        Args:
            characters: Available characters pool
            locations: Available locations pool
            previous_scene: The previous scene data (if any)
            relevant_conversations: Retrieved conversations from vector DB
            
        Returns:
            A dictionary containing the generated scene
        """
        # Update state with current data
        self.state = SceneGeneratorState(
            story=self.story,
            player=self.player,
            characters_pool=characters,
            locations_pool=locations,
            previous_scene=previous_scene,
            relevant_conversations=relevant_conversations or [],
            selected_characters=[]
        )
        
        # Run agent loop
        return await self._run_agent_loop()
        
    async def _run_agent_loop(self) -> Dict[str, Any]:
        """Run the agent loop until the scene is complete"""
        
        # Create system prompt with key components from prompting guide
        system_prompt = """
        You are a scene generator for an AI-driven text adventure game. Your role is to create compelling scenes with characters and locations.
        
        <persistence>
        Keep going until the scene generation is complete. Only terminate when you have selected a location, characters (1-3), and created a scene description.
        </persistence>
        
        <tool_usage>
        Use the generate_location tool to select or create a location, generate_character tool to select or create characters, and finalize_scene tool to complete the scene.
        Only call finalize_scene after you have selected both location and at least one character.
        If you are not sure about what to do next, think step by step and use the appropriate tool.
        </tool_usage>
        
        <planning>
        Plan before each action. Think about what elements would create an interesting scene. Consider:
        1. How this scene connects to previous scenes
        2. What character interactions would be compelling
        3. How to advance the story
        Explain your reasoning for each decision.
        </planning>
        """
        
        # Create initial user prompt with state
        user_prompt = self._create_user_prompt()
        
        # Loop until scene is complete
        scene_complete = False
        step_count = 0
        max_steps = 10
        while not scene_complete and step_count < max_steps:
            # Generate response from LLM with tools
            response = await self.llm.generate_response(
                input_text=user_prompt,
                instructions=system_prompt,
                model=ModelName.GPT_41,
                tools=self.tools,
                temperature=0.7
            )
            
            logging.info(f"Agent step {step_count+1}: Received response from LLM")
            
            # Extract function calls
            function_calls = await LLMService.extract_function_calls(response)
            
            # Process function calls
            if function_calls:
                for call in function_calls:
                    # Update reasoning with the agent's thinking
                    if "reasoning" in call["arguments"]:
                        self.state.reasoning = call["arguments"]["reasoning"]
                        
                    # Handle each tool call
                    if call["name"] == "generate_location":
                        await self._handle_location_generation(call["arguments"])
                        logging.info(f"Agent step {step_count+1}: Generated/selected location: {self.state.selected_location.name if self.state.selected_location else 'None'}")
                    elif call["name"] == "generate_character":
                        await self._handle_character_generation(call["arguments"])
                        logging.info(f"Agent step {step_count+1}: Character count: {len(self.state.selected_characters)}")
                    elif call["name"] == "finalize_scene":
                        self.state.scene_description = call["arguments"]["description"]
                        scene_complete = True
                        logging.info(f"Agent step {step_count+1}: Scene finalized")
                        break
            
            # Update user prompt with new state
            user_prompt = self._create_user_prompt()
            step_count += 1
        
        if step_count >= max_steps and not scene_complete:
            logging.warning(f"Scene generation hit maximum steps ({max_steps}) without completion")
            # Return whatever we have so far
            self.state.scene_description = self.state.scene_description or "Scene generation timed out before completion."
        
        # Return the final scene
        return {
            "location": self.state.selected_location.model_dump() if self.state.selected_location else None,
            "characters": [c.model_dump() for c in self.state.selected_characters],
            "description": self.state.scene_description
        }
    
    async def _handle_location_generation(self, args: Dict[str, Any]) -> None:
        """Handle location generation or selection tool call"""
        
        # Check if we're selecting an existing location
        if "existing_location_id" in args and args["existing_location_id"]:
            # Find location by UUID
            for location in self.state.locations_pool:
                if location.uuid == args["existing_location_id"]:
                    self.state.selected_location = location
                    return
        
        # Otherwise, we need to generate a new location using LocationGenerator
        brief_description = args["brief_description"]
        
        try:
            # Generate a new location using the LocationGenerator
            story_location = await self.location_generator.generate_location(
                story=self.story,
                description=brief_description
            )
            
            # Convert the StoryLocation to a Location
            new_location = Location(
                id=getattr(story_location, 'id', 999),
                name=story_location.name,
                description=story_location.description,
                story_id=self.story.id if self.story.id is not None else 0,
                uuid=getattr(story_location, 'uuid', "new-location-id")
            )
            
            # Set as selected location
            self.state.selected_location = new_location
                
        except Exception as e:
            logging.error(f"Error generating location: {e}")
            # Fallback to a simple location if needed
            self.state.selected_location = Location(
                id=999,
                name=f"Generated: {brief_description[:20]}",
                description=brief_description,
                story_id=self.story.id if self.story.id is not None else 0,
                uuid="fallback-location-id"
            )
    
    async def _handle_character_generation(self, args: Dict[str, Any]) -> None:
        """Handle character generation or selection tool call"""
        
        # Check if we're selecting an existing character
        if "existing_character_id" in args and args["existing_character_id"]:
            # Find character by UUID
            for character in self.state.characters_pool:
                if character.uuid == args["existing_character_id"]:
                    # Add to selected characters if not already present
                    if character not in self.state.selected_characters:
                        # Ensure we don't add more than 3 characters
                        if len(self.state.selected_characters) < 3:
                            current_characters = list(self.state.selected_characters)
                            current_characters.append(character)
                            self.state.selected_characters = current_characters
                    return
        
        # Otherwise, generate a new character if we have a draft
        if "character_draft" in args and args["character_draft"]:
            draft_data = args["character_draft"]
            
            try:
                # Create a CharacterDraft object compatible with the character generator
                from app.schemas.story_generation import CharacterDraft as StoryCharacterDraft
                
                draft = StoryCharacterDraft(
                    name=draft_data["name"],
                    age=draft_data["age"],
                    appearance=draft_data["appearance"],
                    background=draft_data["background"]
                )
                
                # Generate a new character using the CharacterGenerator
                story_character = await self.character_generator.generate_character(
                    character_draft=draft,
                    story=self.story,
                    is_player=False
                )
                
                # Convert the StoryCharacter to a Character
                new_character = Character(
                    id=getattr(story_character, 'id', 999),
                    name=story_character.name,
                    role=story_character.role,
                    description=story_character.description,
                    story_id=self.story.id if self.story.id is not None else 0,
                    backstory=getattr(story_character, 'backstory', None),
                    uuid=getattr(story_character, 'uuid', "new-character-id")
                )
                
                # Add to selected characters if we have fewer than 3
                if len(self.state.selected_characters) < 3:
                    current_characters = list(self.state.selected_characters)
                    current_characters.append(new_character)
                    self.state.selected_characters = current_characters
                        
            except Exception as e:
                logging.error(f"Error generating character: {e}")
                # Fallback to a simple character if needed
                fallback_character = Character(
                    id=999,
                    name=draft_data["name"],
                    role="NPC",
                    description=draft_data["appearance"],
                    story_id=self.story.id if self.story.id is not None else 0,
                    backstory=draft_data["background"],
                    uuid="fallback-character-id"
                )
                if len(self.state.selected_characters) < 3:
                    current_characters = list(self.state.selected_characters)
                    current_characters.append(fallback_character)
                    self.state.selected_characters = current_characters
    
    def _create_user_prompt(self) -> str:
        """Create a user prompt with the current state using XML-style delimiters"""
        
        # Format the selected location
        selected_location_str = "None"
        if self.state.selected_location:
            selected_location_str = f"""
            <name>{self.state.selected_location.name}</name>
            <description>{self.state.selected_location.description}</description>
            <uuid>{self.state.selected_location.uuid}</uuid>
            """
        
        # Format the selected characters
        selected_characters_str = "[]"
        if self.state.selected_characters:
            characters: List[str] = []
            for character in self.state.selected_characters:
                char_str = f"""
                <character>
                    <name>{character.name}</name>
                    <role>{character.role}</role>
                    <description>{character.description}</description>
                    <uuid>{character.uuid}</uuid>
                </character>
                """
                characters.append(char_str)
            selected_characters_str = "".join(characters)
        
        # Format available characters
        available_characters_str = ""
        for character in self.state.characters_pool:
            char_str = f"""
            <character>
                <name>{character.name}</name>
                <role>{character.role}</role>
                <description>{character.description}</description>
                <uuid>{character.uuid}</uuid>
            </character>
            """
            available_characters_str += char_str
        
        # Format available locations
        available_locations_str = ""
        for location in self.state.locations_pool:
            loc_str = f"""
            <location>
                <name>{location.name}</name>
                <description>{location.description}</description>
                <uuid>{location.uuid}</uuid>
            </location>
            """
            available_locations_str += loc_str
        
        # Format the previous scene if available
        previous_scene_str = "None"
        if self.state.previous_scene:
            previous_scene_str = json.dumps(self.state.previous_scene)
        
        # Build the complete prompt with XML delimiters
        return f"""
        <context>
            <story>
                <id>{self.state.story.id}</id>
                <name>{self.state.story.description}</name>
                <description>{self.state.story.description}</description>
            </story>
            
            <player>
                <name>{self.state.player.name}</name>
                <role>{self.state.player.role}</role>
                <description>{self.state.player.description}</description>
            </player>
            
            <previous_scene>{previous_scene_str}</previous_scene>
            
            <current_state>
                <selected_location>
                {selected_location_str}
                </selected_location>
                
                <selected_characters>
                {selected_characters_str}
                </selected_characters>
                
                <scene_description>{self.state.scene_description or "None"}</scene_description>
            </current_state>
            
            <available_characters>
            {available_characters_str}
            </available_characters>
            
            <available_locations>
            {available_locations_str}
            </available_locations>
        </context>
        
        Based on the context above, continue generating the next scene. If you need to generate a location, use the generate_location tool. If you need to generate characters, use the generate_character tool. When you have selected a location and at least one character, use the finalize_scene tool to complete the scene.
        """ 