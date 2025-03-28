from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.orm import Mapped
from typing import List
from app.models.associations import chapter_character_association, scene_character_association, location_character_association


class Character(Base):
    __tablename__ = 'characters'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String) #player or npc
    description = Column(String) # brief description of character
    personality_traits = Column(String) # character's personality traits
    backstory = Column(String) # character's backstory
    goals = Column(String) # character's goals in the story
    speaking_style = Column(String) # character's speaking style, e.g., formal, informal, etc.
    relationships = Column(String) # relationships with other characters
    image_dir = Column(String) # directory where all character images are stored
    image_prompt = Column(String) # this might not be necessary to store in db
    relationship_level = Column(Integer) # on hold for now
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    
    # Relationships
    story = relationship("Story", back_populates="characters")
    messages = relationship("Message", back_populates="character")
    locations: Mapped[List["Location"]] = relationship(secondary=location_character_association, back_populates="characters") # type: ignore
    chapters: Mapped[List["Chapter"]] = relationship(secondary=chapter_character_association, back_populates="characters") # type: ignore
    scenes: Mapped[List["Scene"]] = relationship(secondary=scene_character_association, back_populates="characters") # type: ignore