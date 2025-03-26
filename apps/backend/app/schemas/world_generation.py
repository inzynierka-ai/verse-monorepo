from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# Input models
class CharacterDraft(BaseModel):
    """Base character information to be used for character generation"""
    name: str = Field(...,
                      description="Character name")
    age: int = Field(...,
                     description="Character age")
    appearance: str = Field(...,
                            description="Character appearance")
    background: str = Field(
        ..., description="Character background story")


class WorldInput(BaseModel):
    """World input provided by the user"""
    theme: str = Field(..., description="The emotional or philosophical core concept (e.g., isolation, rebellion, discovery)")
    genre: str = Field(..., description="The storytelling approach or style (e.g., hard sci-fi, fantasy, horror)")
    year: int = Field(...,
                      description="The time period in which the world is set")
    setting: str = Field(..., description="The physical environment specifics (e.g., space station, underwater city, desert outpost)")


class World(BaseModel):
    """World information generated from user input"""
    description: str = Field(...,
                             description="Detailed description of the world")
    rules: List[str] = Field(...,
                             description="Rules or principles of the world")
    prolog: str = Field(...,
                        description="Introductory narrative for the world")


class WorldGenerationInput(BaseModel):
    """Input for generating a world and chapter"""
    world: WorldInput = Field(
        ..., description="World information including theme, genre, year, setting")
    playerCharacter: CharacterDraft = Field(...,
                                            description="Player character information")


class WorldOutput(BaseModel):
    """World output structure"""
    world: World = Field(...,
                         description="Generated world information")


# Character models
class CharacterRelationship(BaseModel):
    """A relationship between characters"""
    name: str = Field(...,
                      description="Name of the related character")
    level: int = Field(...,
                       description="Level or strength of the relationship")
    type: str = Field(...,
                      description="Type of relationship (friend, enemy, etc.)")
    backstory: str = Field(
        ..., description="Backstory of the relationship")


class CharacterFromLLM(BaseModel):
    """Character in the generated world"""
    name: str = Field(...,
                      description="Character name")
    description: str = Field(...,
                             description="Detailed description of the character")
    personalityTraits: Optional[List[str]] = Field(
        None, description="Character's personality traits")
    backstory: str = Field(...,
                           description="Character's backstory")
    goals: List[str] = Field(...,
                             description="Character's goals")
    relationships: List[CharacterRelationship] = Field(
        ..., description="Character's relationships")


class Character(CharacterFromLLM):
    """Final character output structure"""
    imagePrompt: str = Field(...,
                             description="Image generation prompt for this character")
    role: Literal["player", "npc"] = Field(
        ..., description="Character's role in the story (player or npc)")


# Location models

class LocationFromLLM(BaseModel):
    """Location in the generated world"""
    name: str = Field(...,
                      description="Location name")
    description: str = Field(...,
                             description="Detailed description of the location")
    rules: List[str] = Field(...,
                             description="Rules specific to this location")


class Location(LocationFromLLM):
    """Final location output structure"""
    imagePrompt: str = Field(...,
                             description="Image generation prompt for this location")


# Narrator models
class IntroductionOutput(BaseModel):
    """Complete narrative introduction output"""
    steps: List[str] = Field(...,
                             description="List of sequential introduction text steps")
