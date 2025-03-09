from typing import Dict, Any, Optional, List
import asyncio

from app.services.llm import LLMService
from app.utils.websocket_manager import WorldGenWebSocketManager
from app.schemas.world_wizard import (
    WorldSettings,
    CharacterGeneratorInput,
    LocationGeneratorInput,
    ConflictGeneratorInput
)
from app.services.world_generation.world_wizard import WorldWizard
from app.services.world_generation.character_generator import generate_characters
from app.services.world_generation.location_generator import generate_locations
from app.services.world_generation.conflict_generator import generate_conflict
from app.services.world_generation.world_generator import integrate_world_components, format_final_output
from app.services.world_generation.narrator import Narrator
from app.schemas.schemas_ws import (
    StepUpdate, WorldTemplateComplete, CharactersComplete, 
    LocationsComplete, ConflictComplete, WorldComplete,
    NarrationUpdate, NarrationComplete, ErrorMessage
)

class WorldGenerationCoordinator:
    def __init__(self, websocket_manager: WorldGenWebSocketManager, llm_service: Optional[LLMService] = None):
        self.websocket_manager = websocket_manager
        self.llm_service = llm_service or LLMService()
    
    async def generate_world(self, session_id: str, description: str, settings: Optional[Dict[str, Any]] = None):
        """Orchestrate the world generation process, sending updates via WebSocket"""
        try:
            # Create WorldSettings object
            world_settings = WorldSettings(
                description=description,
                **(settings or {})
            )
            
            # Step 1: Generate world template
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="world_template",
                    message="Generating world template...",
                    progress=0.0
                )
            )
            
            world_wizard = WorldWizard(self.llm_service)
            world_template = await world_wizard.create_world_template(world_settings)
            
            await self.websocket_manager.send_message(
                session_id,
                WorldTemplateComplete(
                    type="world_template_complete",
                    data=world_template.model_dump()
                )
            )
            
            # Step 2: Generate characters and locations
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="characters_and_locations",
                    message="Generating characters and locations...",
                    progress=0.2
                )
            )
            
            # Prepare inputs
            character_input = CharacterGeneratorInput(
                world_setting=world_template.setting,
                basic_characters=world_template.basic_characters
            )
            
            location_input = LocationGeneratorInput(
                world_setting=world_template.setting,
                basic_locations=world_template.basic_locations
            )
            
            # Run character and location generation concurrently
            character_task = generate_characters(character_input, self.llm_service)
            location_task = generate_locations(location_input, self.llm_service)
            
            # Await both tasks to complete
            character_output, location_output = await asyncio.gather(character_task, location_task)
            
            detailed_characters = character_output.detailed_characters
            detailed_locations = location_output.detailed_locations
            
            # Send character completion update
            await self.websocket_manager.send_message(
                session_id,
                CharactersComplete(
                    type="characters_complete",
                    data={"characters": [c.model_dump() for c in detailed_characters]}
                )
            )
            
            # Send location completion update  
            await self.websocket_manager.send_message(
                session_id,
                LocationsComplete(
                    type="locations_complete",
                    data={"locations": [l.model_dump() for l in detailed_locations]}
                )
            )
            
            # Step 3: Generate conflict
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="conflict",
                    message="Generating conflict...",
                    progress=0.4
                )
            )
            
            # Prepare character and location summaries
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
            
            conflict_input = ConflictGeneratorInput(
                world_setting=world_template.setting,
                initial_conflict=world_template.initial_conflict,
                character_summaries=character_summaries,
                locations=location_summaries
            )
            
            conflict_output = await generate_conflict(conflict_input, self.llm_service)
            detailed_conflict = conflict_output.detailed_conflict
            
            await self.websocket_manager.send_message(
                session_id,
                ConflictComplete(
                    type="conflict_complete",
                    data=detailed_conflict.model_dump()
                )
            )
            
            # Step 4: Integrate components
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="world_integration",
                    message="Integrating world components...",
                    progress=0.6
                )
            )
            
            final_world = await integrate_world_components(
                world_setting=world_template.setting,
                detailed_characters=detailed_characters,
                detailed_locations=detailed_locations,
                detailed_conflict=detailed_conflict,
                llm_service=self.llm_service
            )
            
            result = format_final_output(
                final_world,
                detailed_characters,
                detailed_locations,
                detailed_conflict
            )
            
            await self.websocket_manager.send_message(
                session_id,
                WorldComplete(
                    type="world_complete",
                    data=result
                )
            )
            
            # Step 5: Generate narration
            await self.websocket_manager.send_message(
                session_id,
                StepUpdate(
                    type="step_update",
                    step="narration",
                    message="Creating narration...",
                    progress=0.8
                )
            )
            
            narrator = Narrator(result, self.llm_service)
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