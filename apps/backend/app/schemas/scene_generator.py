from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.story_generation import Story, Location, Character, Scene

class SceneGeneratorState(BaseModel):
    """State model for the Scene Generator Agent"""
    story: Story
    player: Character
    characters_pool: List[Character]  # All available characters
    locations_pool: List[Location]  # All available locations
    previous_scene: Optional[Scene] = None
    
    # Selected elements for the new scene
    selected_location: Optional[Location] = None
    selected_characters: List[Character] = Field(default_factory=list)
    
    # Output building
    scene_description: Optional[str] = None
    
    # Memory context
    relevant_conversations: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Tool error messages
    location_generation_error: Optional[str] = None
    character_generation_error: Optional[str] = None
    finalize_scene_error: Optional[str] = None 

class SceneGenerationResult(BaseModel):
    """Result model for the Scene Generator Agent"""
    location: Location
    characters: List[Character]
    description: str
    steps_taken: int 