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


class StoryInput(BaseModel):
    """Story input provided by the user"""
    theme: str = Field(..., description="The emotional or philosophical core concept (e.g., isolation, rebellion, discovery)")
    genre: str = Field(..., description="The storytelling approach or style (e.g., hard sci-fi, fantasy, horror)")
    year: int = Field(...,
                      description="The time period in which the story is set")
    setting: str = Field(..., description="The physical environment specifics (e.g., space station, underwater city, desert outpost)")


class Story(BaseModel):
    description: str
    rules: List[str]
    user_id: Optional[int] = None
    title: str
    uuid: Optional[str] = None
    id: Optional[int] = None  # Add this field

class StoryGenerationInput(BaseModel):
    """Input for generating a story"""
    story: StoryInput = Field(
        ..., description="Story information including theme, genre, year, setting")
    playerCharacter: CharacterDraft = Field(...,
                                            description="Player character information")


class StoryOutput(BaseModel):
    """Story output structure"""
    story: Story = Field(...,
                         description="Generated story information")


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
    """Character in the generated story"""
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
    imageUrl: str = Field(...,
                         description="URL of the generated image for this character")
    role: Literal["player", "npc"] = Field(
        ..., description="Character's role in the story (player or npc)")
    uuid: str = Field(
        ..., description="Unique identifier for the character")


# Location models

class LocationFromLLM(BaseModel):
    """Location in the generated story"""
    name: str = Field(...,
                      description="Location name")
    description: str = Field(...,
                             description="Detailed description of the location")
    rules: List[str] = Field(...,
                             description="Rules specific to this location")


class Location(LocationFromLLM):
    """Final location output structure"""
    id: Optional[int] = Field(None,
                               description="Location ID in the database")
    imageUrl: str = Field(...,
                         description="URL of the generated image for this location")
    uuid: str = Field(
        ..., description="Unique identifier for the location")


# Narrator models
class IntroductionOutput(BaseModel):
    """Complete narrative introduction output"""
    steps: List[str] = Field(...,
                             description="List of sequential introduction text steps")

class Scene(BaseModel):
    """Scene in the generated story"""
    location: Location = Field(...,
                              description="Location of the scene")
    characters: List[Character] = Field(...,
                                        description="Characters in the scene")
    description: str = Field(...,
                             description="Description of the scene")
    summary: str = Field(...,
                         description="Summary of the scene")
