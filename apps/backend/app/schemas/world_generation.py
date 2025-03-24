from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# Input models
class PlayerCharacterInput(BaseModel):
    """Player character information provided by the user"""
    name: str = Field(..., description="Character name")
    age: int = Field(..., description="Character age")
    appearance: str = Field(..., description="Character appearance")
    background: str = Field(..., description="Character background story")


class WorldInput(BaseModel):
    """World input provided by the user"""
    theme: str = Field(..., description="The emotional or philosophical core concept (e.g., isolation, rebellion, discovery)")
    genre: str = Field(..., description="The storytelling approach or style (e.g., hard sci-fi, fantasy, horror)")
    year: int = Field(..., description="The time period in which the world is set")
    setting: str = Field(..., description="The physical environment specifics (e.g., space station, underwater city, desert outpost)")


class World(BaseModel):
    """World information generated from user input"""
    description: str = Field(..., description="Detailed description of the world")
    rules: List[str] = Field(..., description="Rules or principles of the world")
    prolog: str = Field(..., description="Introductory narrative for the world")


class WorldGenerationInput(BaseModel):
    """Input for generating a world and chapter"""
    world: WorldInput = Field(..., description="World information including theme, genre, year, setting")
    playerCharacter: PlayerCharacterInput = Field(..., description="Player character information")


class WorldOutput(BaseModel):
    """World output structure"""
    world: World = Field(..., description="Generated world information")


# Character models
class CharacterRelationship(BaseModel):
    """A relationship between characters"""
    id: str = Field(..., description="ID of the related character")
    level: int = Field(..., description="Level or strength of the relationship")
    type: str = Field(..., description="Type of relationship (friend, enemy, etc.)")
    backstory: str = Field(..., description="Backstory of the relationship")


class Character(BaseModel):
    """Character in the generated world"""
    id: str = Field(..., description="Unique identifier for the character")
    name: str = Field(..., description="Character name")
    role: Literal["player", "npc"] = Field(..., description="Character's role in the story (player or npc)")
    description: str = Field(..., description="Detailed description of the character")
    personalityTraits: Optional[List[str]] = Field(None, description="Character's personality traits")
    backstory: str = Field(..., description="Character's backstory")
    goals: List[str] = Field(..., description="Character's goals")
    relationships: List[CharacterRelationship] = Field(..., description="Character's relationships")
    connectedLocations: List[str] = Field(..., description="IDs of locations this character is connected to")
    imagePrompt: Optional[str] = Field(None, description="Image generation prompt for this character")


class CharacterWithImagePrompt(BaseModel):
    """Character with image prompt for image generation"""
    id: str = Field(..., description="Unique identifier for the character")
    imagePrompt: str = Field(..., description="Image generation prompt for this character")


class CharactersOutput(BaseModel):
    """Characters output structure"""
    characters: List[Character] = Field(..., description="List of generated characters")


class CharacterImagePromptsOutput(BaseModel):
    """Character image prompts output structure"""
    characters: List[CharacterWithImagePrompt] = Field(..., description="List of character image prompts")


# Location models
class Location(BaseModel):
    """Location in the generated world"""
    id: str = Field(..., description="Unique identifier for the location")
    name: str = Field(..., description="Location name")
    description: str = Field(..., description="Detailed description of the location")
    connectedLocations: List[str] = Field(..., description="IDs of connected locations")
    connectedCharacters: List[str] = Field(..., description="IDs of characters connected to this location")
    rules: List[str] = Field(..., description="Rules specific to this location")
    imagePrompt: Optional[str] = Field(None, description="Image generation prompt for this location")


class LocationWithImagePrompt(BaseModel):
    """Location with image prompt for image generation"""
    id: str = Field(..., description="Unique identifier for the location")
    imagePrompt: str = Field(..., description="Image generation prompt for this location")


class LocationsOutput(BaseModel):
    """Locations output structure"""
    locations: List[Location] = Field(..., description="List of generated locations")


class LocationImagePromptsOutput(BaseModel):
    """Location image prompts output structure"""
    locations: List[LocationWithImagePrompt] = Field(..., description="List of location image prompts")


# Possible endings models
class PossibleEnding(BaseModel):
    """Possible ending for a chapter"""
    trigger: str = Field(..., description="Event or condition that triggers this ending")
    result: str = Field(..., description="What happens as a result of this ending")


class PossibleEndingsOutput(BaseModel):
    """Possible endings output structure"""
    possibleEndings: List[PossibleEnding] = Field(..., description="List of possible endings for the chapter")


# Narrator models
class IntroductionOutput(BaseModel):
    """Complete narrative introduction output"""
    steps: List[str] = Field(..., description="List of sequential introduction text steps")


# Aggregate output model
class ChapterOutput(BaseModel):
    """Complete chapter output including all components"""
    world: World = Field(..., description="World information")
    characters: List[Character] = Field(..., description="List of characters")
    locations: List[Location] = Field(..., description="List of locations")
    possibleEndings: List[PossibleEnding] = Field(..., description="List of possible endings")
