from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Basic templates (from World Wizard)
class CharacterTemplate(BaseModel):
    """Base template for a character in the game world"""
    id: str = Field(..., description="Unique identifier for the character")
    name: str = Field(..., description="Character name")
    role: str = Field(..., description="Character's role in the story")
    brief: str = Field(..., description="Brief description of the character")
    appearance_hint: Optional[str] = Field(None, description="Hint about the character's appearance")


class LocationTemplate(BaseModel):
    """Base template for a location in the game world"""
    id: str = Field(..., description="Unique identifier for the location")
    name: str = Field(..., description="Location name")
    brief: str = Field(..., description="Brief description of the location")
    appearance_hint: Optional[str] = Field(None, description="Hint about the location's appearance")


class ConflictTemplate(BaseModel):
    """Template for the initial conflict in the game world"""
    description: str = Field(..., description="Description of the conflict")
    trigger_event: Optional[str] = Field(None, description="The event that triggers the conflict")


class SettingInfo(BaseModel):
    """Information about the world setting"""
    theme: str = Field(..., description="The primary theme of the world")
    atmosphere: Optional[str] = Field(None, description="The emotional atmosphere or tone")
    description: str = Field(..., description="Brief description of the setting")


class WorldSettings(BaseModel):
    """Settings for generating a world."""
    description: str = Field(..., description="A detailed description of the world to generate")
    additional_context: Optional[str] = Field(None, description="Any additional context for world generation")


class WorldDescription(BaseModel):
    """A detailed text description of a world."""
    content: str = Field(..., description="The world description content")


class WorldTemplate(BaseModel):
    """Complete template for a game world"""
    setting: SettingInfo
    basic_characters: List[CharacterTemplate] = Field(..., description="List of character templates")
    basic_locations: List[LocationTemplate] = Field(..., description="List of location templates")
    initial_conflict: ConflictTemplate


# Detailed models (for specialized agents)
class PersonalityTrait(BaseModel):
    """A personality trait of a character"""
    name: str = Field(..., description="Name of the trait")
    description: str = Field(..., description="Description of how this trait manifests")


class Relationship(BaseModel):
    """A relationship between characters"""
    target_id: str = Field(..., description="ID of the related character")
    type: str = Field(..., description="Type of relationship (friend, enemy, etc.)")
    description: str = Field(..., description="Description of the relationship")


class DetailedCharacter(BaseModel):
    """Detailed character with expanded information"""
    id: str = Field(..., description="Unique identifier for the character")
    name: str = Field(..., description="Character name")
    role: str = Field(..., description="Character's role in the story")
    description: str = Field(..., description="Detailed description of the character")
    personality_traits: List[str] = Field(..., description="Character's personality traits as simple strings")
    backstory: str = Field(..., description="Character's backstory")
    goals: List[str] = Field(..., description="Character's goals")
    relationships: Optional[List[Relationship]] = Field(None, description="Character's relationships")
    appearance: str = Field(..., description="Detailed description of the character's appearance")
    connected_locations: Optional[List[str]] = Field(None, description="IDs of locations this character is connected to")
    image_prompt: Optional[str] = Field("", description="Image generation prompt for this character")


class InteractiveElement(BaseModel):
    """An interactive element within a location"""
    name: str = Field(..., description="Name of the element")
    description: str = Field(..., description="Description of the element")
    interaction: str = Field(..., description="Possible interaction with the element")


class DetailedLocation(BaseModel):
    """Detailed location with expanded information"""
    id: str = Field(..., description="Unique identifier for the location")
    name: str = Field(..., description="Location name")
    description: str = Field(..., description="Detailed description of the location")
    history: str = Field(..., description="History of the location")
    atmosphere: str = Field(..., description="Atmosphere of the location")
    interactive_elements: List[InteractiveElement] = Field(..., description="Interactive elements in the location")
    connected_locations: Optional[List[str]] = Field(None, description="IDs of connected locations")


class Faction(BaseModel):
    """A faction or group involved in a conflict"""
    name: str = Field(..., description="Name of the faction")
    motivation: str = Field(..., description="What this faction wants")
    methods: str = Field(..., description="How this faction pursues its goals")


class Resolution(BaseModel):
    """A possible resolution path for a conflict"""
    path: str = Field(..., description="Name of the resolution approach")
    description: str = Field(..., description="How this resolution would work")
    consequences: str = Field(..., description="Potential aftermath of this resolution")


class TurningPoint(BaseModel):
    """A turning point or escalation trigger in a conflict"""
    trigger: str = Field(..., description="Event or condition that escalates the conflict")
    result: str = Field(..., description="How the conflict changes after this point")


class EntityConnection(BaseModel):
    """A connection between a conflict and another entity (character or location)"""
    entity_id: str = Field(..., description="ID of the connected entity")
    connection: str = Field(..., description="Description of the connection")


class DetailedConflict(BaseModel):
    """Detailed conflict with expanded information"""
    title: str = Field(..., description="A short, evocative title for the conflict")
    description: str = Field(..., description="Detailed description of the conflict")
    factions: List[Faction] = Field(..., description="Factions or groups involved in the conflict")
    possible_resolutions: List[Resolution] = Field(..., description="Possible ways the conflict could be resolved")
    turning_points: List[TurningPoint] = Field(..., description="Potential escalation points or turning points")
    character_connections: List[EntityConnection] = Field(..., description="Connections to characters")
    location_connections: List[EntityConnection] = Field(..., description="Connections to locations")
    personal_stakes: str = Field(..., description="What individuals stand to gain or lose")
    community_stakes: str = Field(..., description="How the conflict affects communities")
    world_stakes: str = Field(..., description="Broader implications for the setting")


class VisualAsset(BaseModel):
    """Visual asset for a character or location"""
    id: str = Field(..., description="ID of the character or location")
    image_url: str = Field(..., description="URL to the image")
    style: str = Field(..., description="Visual style of the image")
    description: str = Field(..., description="Description of what the image depicts")


# World Coordinator models
class CharacterConnection(BaseModel):
    """Connection information for a character in the coordinated world"""
    character_id: str = Field(..., description="ID of the character")
    connected_locations: List[str] = Field(..., description="IDs of locations this character is connected to")
    involvement_in_conflict: str = Field(..., description="How this character relates to the main conflict")


class LocationConnection(BaseModel):
    """Connection information for a location in the coordinated world"""
    location_id: str = Field(..., description="ID of the location")
    connected_characters: List[str] = Field(..., description="IDs of characters connected to this location")
    role_in_conflict: str = Field(..., description="How this location relates to the main conflict")


class StoryHook(BaseModel):
    """A potential story hook or scenario for gameplay"""
    title: str = Field(..., description="Title of the story hook")
    description: str = Field(..., description="Description of the potential story or scenario")
    involving_characters: List[str] = Field(..., description="Character IDs relevant to this hook")
    involving_locations: List[str] = Field(..., description="Location IDs relevant to this hook")


class WorldRule(BaseModel):
    """A rule or principle that governs the world"""
    name: str = Field(..., description="Name of the rule or principle")
    description: str = Field(..., description="Explanation of how this rule functions in the world")


class FinalGameWorld(BaseModel):
    """The final, fully coordinated game world"""
    setting_summary: str = Field(..., description="A concise summary of the world setting")
    character_connections: List[CharacterConnection] = Field(..., description="Connection information for characters")
    location_connections: List[LocationConnection] = Field(..., description="Connection information for locations")
    story_hooks: List[StoryHook] = Field(..., description="Potential story hooks for gameplay")
    world_rules: List[WorldRule] = Field(..., description="Rules or principles of the world")
    cohesion_notes: str = Field(..., description="Notes on how the elements fit together")


# Aggregate Models
class CharacterGeneratorInput(BaseModel):
    """Input for the Character Generator"""
    world_setting: SettingInfo = Field(..., description="World setting information")
    basic_characters: List[CharacterTemplate] = Field(..., description="Basic character templates to expand")


class CharacterGeneratorOutput(BaseModel):
    """Output from the Character Generator"""
    detailed_characters: List[DetailedCharacter] = Field(..., description="Detailed character profiles")


class LocationGeneratorInput(BaseModel):
    """Input for the Location Generator"""
    world_setting: SettingInfo = Field(..., description="World setting information")
    basic_locations: List[LocationTemplate] = Field(..., description="Basic location templates to expand")


class LocationGeneratorOutput(BaseModel):
    """Output from the Location Generator"""
    detailed_locations: List[DetailedLocation] = Field(..., description="Detailed location descriptions")


class ConflictGeneratorInput(BaseModel):
    """Input for the Conflict Generator"""
    world_setting: SettingInfo = Field(..., description="World setting information")
    initial_conflict: ConflictTemplate = Field(..., description="Initial conflict to expand")
    character_summaries: List[Dict[str, str]] = Field(..., description="Brief summaries of characters")
    locations: Optional[List[Dict[str, str]]] = Field(None, description="Brief summaries of locations")


class ConflictGeneratorOutput(BaseModel):
    """Output from the Conflict Generator"""
    detailed_conflict: DetailedConflict = Field(..., description="Detailed conflict description")


class VisualGeneratorInput(BaseModel):
    """Input for the Visual Generator"""
    detailed_characters: List[DetailedCharacter] = Field(..., description="Detailed character profiles")
    detailed_locations: List[DetailedLocation] = Field(..., description="Detailed location descriptions")


class VisualGeneratorOutput(BaseModel):
    """Output from the Visual Generator"""
    character_visuals: List[VisualAsset] = Field(..., description="Visual assets for characters")
    location_visuals: List[VisualAsset] = Field(..., description="Visual assets for locations")


class WorldCoordinatorInput(BaseModel):
    """Input for the World Coordinator"""
    world_setting: SettingInfo = Field(..., description="World setting information")
    detailed_characters: List[DetailedCharacter] = Field(..., description="Detailed character profiles")
    detailed_locations: List[DetailedLocation] = Field(..., description="Detailed location descriptions")
    detailed_conflict: DetailedConflict = Field(..., description="Detailed conflict description")
    character_visuals: Optional[List[VisualAsset]] = Field(None, description="Visual assets for characters")
    location_visuals: Optional[List[VisualAsset]] = Field(None, description="Visual assets for locations")


class WorldCoordinatorOutput(BaseModel):
    """Output from the World Coordinator"""
    final_game_world: FinalGameWorld = Field(..., description="The final, coordinated game world")


# Request models for API endpoints
class WorldGenerationRequest(BaseModel):
    """Request to generate a world description"""
    theme: str = Field(..., description="The primary theme or concept for the world")


class WorldJsonRequest(BaseModel):
    """Request to generate a structured JSON representation of a world"""
    description: str = Field(..., description="Textual description of the game world")


class GenerateCompleteWorldRequest(BaseModel):
    """Request to generate a complete world through the entire pipeline"""
    theme: str = Field(..., description="The primary theme or concept for the world")
    include_visuals: bool = Field(False, description="Whether to include visual assets")
    style_preference: Optional[str] = Field(None, description="Preferred visual style") 