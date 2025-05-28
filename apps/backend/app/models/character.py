from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.orm import Mapped
from typing import List
from app.models.associations import scene_character_association


class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)  # player or npc
    description = Column(String)  # brief description of character
    # shorter 3-4 sentence description for UI display
    brief_description = Column(String)
    personality_traits = Column(String)  # character's personality traits
    backstory = Column(String)  # character's backstory
    goals = Column(String)  # character's goals in the story
    # character's speaking style, e.g., formal, informal, etc.
    speaking_style = Column(String)
    image_dir = Column(String)  # directory where all character images are stored
    image_prompt = Column(String)  # this might not be necessary to store in db
    relationship_level = Column(Integer)  # relationship level with the player character
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    uuid = Column(String, nullable=False)
    immediate_goals = Column(String, nullable=True)  # Character's immediate goals

    # Relationships
    story = relationship("Story", back_populates="characters")
    messages = relationship("Message", back_populates="character")
    scenes: Mapped[List["Scene"]] = relationship(
        secondary=scene_character_association, back_populates="characters")  # type: ignore
    memories = relationship(
        "CharacterMemory", back_populates="character", lazy="dynamic")
