from typing import Dict, Any, Optional, List
import asyncio

from app.services.llm import LLMService
from app.utils.websocket_manager import WorldGenWebSocketManager
from app.schemas.world_generation import (
    WorldSettings,
    CharacterGeneratorInput,
    LocationGeneratorInput
)
from app.schemas.schemas_ws import WorldGenerationInput
from app.services.world_generation.world_generator import WorldGenerator
from app.services.world_generation.chapter_generator import generate_chapter
from app.services.world_generation.character_generator import generate_characters
from app.services.world_generation.location_generator import generate_locations
from app.services.world_generation.possible_endings_generator import generate_possible_endings
from app.services.world_generation.narrator import Narrator
from app.schemas.schemas_ws import (
    StepUpdate, WorldTemplateComplete, ChapterComplete, CharactersComplete, 
    LocationsComplete, PossibleEndingsComplete, WorldComplete,
    NarrationUpdate, NarrationComplete, ErrorMessage, ImagePromptUpdate
)

class WorldGenerationCoordinator:
    def __init__(self, websocket_manager: WorldGenWebSocketManager, llm_service: Optional[LLMService] = None):
        self.websocket_manager = websocket_manager
        self.llm_service = llm_service or LLMService()
    
    async def generate_world(
        self, 
        session_id: str, 
        input_data: WorldGenerationInput
    ):
        """
        Orchestrate the world generation process, sending updates via WebSocket
        
        Args:
            session_id: ID for the WebSocket session
            input_data: Structured input with world and player character details
        """
        try:
            # Extract world information
            world_info = input_data.world.model_dump()
            player_info = input_data.playerCharacter.model_dump() if input_data.playerCharacter else {}
            
            # Create description from world info
            description_parts = [
                f"Theme: {world_info['theme']}",
                f"Genre: {world_info['genre']}",
                f"Year: {world_info['year']}",
                f"Setting: {world_info['setting']}"
            ]
                
            description = ". ".join(description_parts)
            
            # Add player character as additional context
            additional_context = ""
            if player_info:
                player_parts = [
                    f"Name: {player_info['name']}",
                    f"Age: {player_info['age']}",
                    f"Appearance: {player_info['appearance']}",
                    f"Background: {player_info['background']}"
                ]
                
                additional_context = "Player Character: " + ". ".join(player_parts)
            
            # Create WorldSettings object
            world_settings = WorldSettings(
                description=description,
                additional_context=additional_context
            )
            
            # Step 1: Generate world template (free world description and JSON conversion)
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="world_template",
                    message="Generating world description...",
                    progress=0.0
                )
            )
            
            world_generator = WorldGenerator(self.llm_service)
            world_template = await world_generator.create_world_template(world_settings)
            
            world_json = {
                "world": {
                    "description": world_template.setting.description,
                    "rules": [rule.description for rule in world_template.setting.rules],
                    "prolog": world_template.setting.backstory
                }
            }
            
            await self.websocket_manager.send_message(
                session_id,
                WorldTemplateComplete(
                    type="world_template_complete",
                    data=world_json
                )
            )
            
            # Step 2: Generate chapter overview using Hero's Journey
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="chapter_overview",
                    message="Creating chapter overview...",
                    progress=0.15
                )
            )
            
            chapter_result = await generate_chapter(world_json, chapter_number=1, llm_service=self.llm_service)
            chapter_overview = chapter_result["chapterOverview"]
            
            await self.websocket_manager.send_message(
                session_id,
                ChapterComplete(
                    type="chapter_complete",
                    data={"chapterOverview": chapter_overview}
                )
            )
            
            # Step 3: Generate characters and locations based on the chapter overview
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="characters_and_locations",
                    message="Generating characters and locations...",
                    progress=0.25
                )
            )
            
            # Prepare inputs for character generation
            character_input = CharacterGeneratorInput(
                world_setting=world_template.setting,
                basic_characters=world_template.basic_characters,
                chapter_overview=chapter_overview  # Add chapter context
            )
            
            location_input = LocationGeneratorInput(
                world_setting=world_template.setting,
                basic_locations=world_template.basic_locations,
                chapter_overview=chapter_overview  # Add chapter context
            )
            
            # Run character and location generation concurrently
            character_task = generate_characters(character_input, self.llm_service)
            location_task = generate_locations(location_input, self.llm_service)
            
            # Await both tasks to complete
            character_output, location_output = await asyncio.gather(character_task, location_task)
            
            detailed_characters = character_output.detailed_characters
            detailed_locations = location_output.detailed_locations
            
            # Step a: Convert to JSON (without the imagePrompt)
            characters_json = {
                "characters": [
                    {
                        "id": char.id,
                        "name": char.name,
                        "role": char.role,
                        "description": char.description,
                        "personalityTraits": char.personality_traits,
                        "backstory": char.backstory,
                        "goals": char.goals,
                        "relationships": [
                            {
                                "id": rel.target_id,
                                "level": rel.relationship_level,
                                "type": rel.relationship_type,
                                "backstory": rel.backstory
                            } for rel in char.relationships
                        ],
                        "connectedLocations": char.connected_locations
                    } for char in detailed_characters
                ]
            }
            
            locations_json = {
                "locations": [
                    {
                        "id": loc.id,
                        "name": loc.name,
                        "description": loc.description,
                        "connectedLocations": loc.connected_locations,
                        "connectedCharacters": loc.connected_characters,
                        "rules": [rule.description for rule in loc.rules] if loc.rules else []
                    } for loc in detailed_locations
                ]
            }
            
            # Send character and location completion updates
            await self.websocket_manager.send_message(
                session_id,
                CharactersComplete(
                    type="characters_complete",
                    data=characters_json
                )
            )
            
            await self.websocket_manager.send_message(
                session_id,
                LocationsComplete(
                    type="locations_complete",
                    data=locations_json
                )
            )
            
            # Step 3b: Generate image prompts for characters and locations in parallel
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="image_prompts",
                    message="Generating visual descriptions...",
                    progress=0.35
                )
            )
            
            # We'll simulate image prompt generation here
            # In a real implementation, you'd have a specialized class for this
            # Here we're assuming the image prompts are already part of the character/location objects
            character_image_prompts = []
            for char in detailed_characters:
                # In real implementation, you'd generate this with an LLM call
                image_prompt = f"A detailed portrait of {char.name}, a {char.role} in a fantasy setting. {char.description}"
                character_image_prompts.append({
                    "id": char.id,
                    "imagePrompt": image_prompt
                })
                
                # Send update for each image prompt
                await self.websocket_manager.send_message(
                    session_id,
                    ImagePromptUpdate(
                        type="image_prompt_update",
                        entity_type="character",
                        entity_id=char.id,
                        prompt=image_prompt
                    )
                )
            
            location_image_prompts = []
            for loc in detailed_locations:
                # In real implementation, you'd generate this with an LLM call
                image_prompt = f"A wide-angle view of {loc.name}, a location described as: {loc.description}"
                location_image_prompts.append({
                    "id": loc.id,
                    "imagePrompt": image_prompt
                })
                
                # Send update for each image prompt
                await self.websocket_manager.send_message(
                    session_id,
                    ImagePromptUpdate(
                        type="image_prompt_update",
                        entity_type="location",
                        entity_id=loc.id,
                        prompt=image_prompt
                    )
                )
            
            # Step 4: Generate possible endings
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="possible_endings",
                    message="Generating possible story endings...",
                    progress=0.50
                )
            )
            
            # Prepare character and location summaries for the endings generator
            character_summaries = []
            for char in detailed_characters:
                character_summaries.append({
                    "id": char.id,
                    "name": char.name,
                    "role": char.role,
                    "description": char.description
                })
            
            location_summaries = []
            for loc in detailed_locations:
                location_summaries.append({
                    "id": loc.id,
                    "name": loc.name,
                    "description": loc.description
                })
            
            # Generate possible endings
            possible_endings_result = await generate_possible_endings(
                chapter_overview, 
                character_summaries, 
                location_summaries,
                self.llm_service
            )
            
            await self.websocket_manager.send_message(
                session_id,
                PossibleEndingsComplete(
                    type="possible_endings_complete",
                    data=possible_endings_result
                )
            )
            
            # Step 5: Integrate all components for the final world
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="world_integration",
                    message="Assembling final world...",
                    progress=0.75
                )
            )
            
            # Combine all components into a single structure
            final_world = {
                "world": world_json["world"],
                "characters": characters_json["characters"],
                "locations": locations_json["locations"],
                "possibleEndings": possible_endings_result["possibleEndings"]
            }
            
            await self.websocket_manager.send_message(
                session_id,
                WorldComplete(
                    type="world_complete",
                    data=final_world
                )
            )
            
            # Step 6: Generate narration (5-step introduction)
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="narration",
                    message="Creating 5-step introduction...",
                    progress=0.85
                )
            )
            
            narrator = Narrator(final_world, self.llm_service)
            introduction_steps = await narrator.generate_introduction()
            
            # Send each narration step as it's generated
            for i, step in enumerate(introduction_steps):
                await self.websocket_manager.send_message(
                    session_id,
                    NarrationUpdate(
                        type="narration_update",
                        step=step["title"],
                        content=step["content"]
                    )
                )
            
            # Send final completion message
            await self.websocket_manager.send_message(
                session_id,
                NarrationComplete(
                    type="narration_complete",
                    data={"introduction": introduction_steps}
                )
            )
            
        except Exception as e:
            # Handle errors
            await self.websocket_manager.send_message(
                session_id,
                ErrorMessage(
                    type="error",
                    message="Error during world generation",
                    details=str(e)
                )
            )
            raise 