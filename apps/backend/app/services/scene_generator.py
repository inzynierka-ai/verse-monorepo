import json
from typing import List, Dict, Any, Optional, Coroutine
import logging
import asyncio

from app.services.llm import LLMService, ModelName
from app.schemas.scene_generator import SceneGeneratorState
from app.services.game_engine.tools.location_generator import LocationGenerator
from app.services.game_engine.tools.character_generator import CharacterGenerator
from app.schemas.story_generation import Story, Location, Character
from langfuse.decorators import observe  # type: ignore
from langfuse import Langfuse  # type: ignore


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
        self.langfuse = Langfuse()
        
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
                        "description": "Brief description to guide location generation when introducing a new location"
                    },
                    "existing_location_id": {
                        "type": "string", 
                        "description": "UUID of existing location to use (optional)"
                    }
                },
                "required": []
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
                    }
                },
                "required": []
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
                },
                "required": ["description"]
            }
        })
        
        return [location_generator, character_generator, finalize_scene]
        
    @observe(name="generate_scene")
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
        
    @observe(name="agent_loop")
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

        <character_generation_rules>
        NEVER generate or modify the player character. The player character is already defined in the context and must remain unchanged.
        Only generate or select NPCs (non-player characters) that are DIFFERENT from the player.
        The player character information is provided for context only.
        </character_generation_rules>
        
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
            
            step_count += 1
            
            # Generate response from LLM with tools
            logging.info(f"Agent step {step_count}: Generating LLM response")
            logging.info(f"Current state: {self.state}")
            
            # This will be traced by LLMService's @observe decorator
            response = await self.llm.generate_response(
                input_text=user_prompt,
                instructions=system_prompt,
                model=ModelName.GPT_41,
                tools=self.tools,
                temperature=0.7,
                metadata={"step": str(step_count), "max_steps": str(max_steps)}
            )
            
            logging.info(f"Agent step {step_count}: Received response from LLM")
            
            # Extract function calls
            function_calls = await LLMService.extract_function_calls(response)
            
            # Process function calls
            if function_calls:
                # Group function calls by type
                location_calls = [call for call in function_calls if call["name"] == "generate_location"]
                character_calls = [call for call in function_calls if call["name"] == "generate_character"]
                finalize_calls = [call for call in function_calls if call["name"] == "finalize_scene"]
                
                # Process location and character calls in parallel
                tasks: List[Coroutine[Any, Any, None]] = []
                for call in location_calls:
                    tasks.append(self._handle_location_generation(call["arguments"]))
                for call in character_calls:
                    tasks.append(self._handle_character_generation(call["arguments"]))
                
                if tasks:
                    await asyncio.gather(*tasks)
                    
                    # Log results after parallel processing
                    if location_calls:
                        location_name = self.state.selected_location.name if self.state.selected_location else "None"
                        logging.info(f"Agent step {step_count}: Generated/selected location: {location_name}")
                    if character_calls:
                        logging.info(f"Agent step {step_count}: Character count: {len(self.state.selected_characters)}")
                
                # Process finalize calls sequentially
                for call in finalize_calls:
                    # Clear any previous error
                    self.state.finalize_scene_error = None
                    try:
                        self.state.scene_description = call["arguments"]["description"]
                        scene_complete = True
                        logging.info(f"Agent step {step_count}: Scene finalized")
                        break
                    except Exception as e:
                        error_msg = f"Error finalizing scene: {e}"
                        logging.error(error_msg)
                        self.state.finalize_scene_error = error_msg
            
            # Update user prompt with new state
            user_prompt = self._create_user_prompt()
        
        if step_count >= max_steps and not scene_complete:
            logging.warning(f"Scene generation hit maximum steps ({max_steps}) without completion")
            # Return whatever we have so far
            self.state.scene_description = self.state.scene_description or "Scene generation timed out before completion."
        
        # Return the final scene
        return {
            "location": self.state.selected_location.model_dump() if self.state.selected_location else None,
            "characters": [c.model_dump() for c in self.state.selected_characters],
            "description": self.state.scene_description,
            "steps_taken": step_count
        }
    
    @observe(name="handle_location_generation")
    async def _handle_location_generation(self, args: Dict[str, Any]) -> None:
        """Handle location generation or selection tool call"""
        
        # Clear previous error
        self.state.location_generation_error = None
        
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
            new_location = await self.location_generator.generate_location(
                story=self.story,
                description=brief_description
            )

            
            # Set as selected location
            self.state.selected_location = new_location
                
        except Exception as e:
            error_msg = f"Error generating location: {e}"
            logging.error(error_msg)
            self.state.location_generation_error = error_msg

    
    @observe(name="handle_character_generation")
    async def _handle_character_generation(self, args: Dict[str, Any]) -> None:
        """Handle character generation or selection tool call"""
        
        # Clear previous error
        self.state.character_generation_error = None
        
        # Check if we're selecting an existing character
        if "existing_character_id" in args and args["existing_character_id"]:
            # Find character by UUID
            for character in self.state.characters_pool:
                if character.uuid == args["existing_character_id"]:
                    # Prevent selecting character with same name as player
                    if character.name == self.player.name or character.role == "player":
                        error_msg = f"Cannot select character with same name or role as player"
                        logging.error(error_msg)
                        self.state.character_generation_error = error_msg
                        return
                        
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
            
            # Prevent generating character with same name as player
            if draft_data["name"] == self.player.name or draft_data.get("role") == "player":
                error_msg = f"Cannot generate character with same name or role as player"
                logging.error(error_msg)
                self.state.character_generation_error = error_msg
                return
                
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
                new_character = await self.character_generator.generate_character(
                    character_draft=draft,
                    story=self.story,
                    is_player=False
                )
                
                logging.info(f"new_character: {new_character}")
                # Add to selected characters if we have fewer than 3
                if len(self.state.selected_characters) < 3:
                    current_characters = list(self.state.selected_characters)
                    current_characters.append(new_character)
                    self.state.selected_characters = current_characters
                        
            except Exception as e:
                error_msg = f"Error generating character: {e}"
                logging.error(error_msg)
                self.state.character_generation_error = error_msg
                
    
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
        
        # Format error messages
        error_messages = ""
        if self.state.location_generation_error:
            error_messages += f"<location_error>{self.state.location_generation_error}</location_error>\n"
        if self.state.character_generation_error:
            error_messages += f"<character_error>{self.state.character_generation_error}</character_error>\n"
        if self.state.finalize_scene_error:
            error_messages += f"<finalize_error>{self.state.finalize_scene_error}</finalize_error>\n"
        
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
                
                <errors>
                {error_messages}
                </errors>
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