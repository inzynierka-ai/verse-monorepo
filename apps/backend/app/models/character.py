from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.orm import Mapped
from typing import List
from app.models.associations import chapter_character_association, scene_character_association


class Character(Base):
    __tablename__ = 'characters'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    description = Column(String, nullable=False) # brief description of character
    details = Column(String, nullable=False) # incl. physical description, personality traits, backstory, goals, relationships
    image_dir = Column(String, nullable=True) # directory where all character images are stored
    image_prompt = Column(String, nullable=True) # this might not be necessary to store in db
    relationship_level = Column(Integer, nullable=False) # on hold for now
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    
    # Relationships
    story = relationship("Story", back_populates="characters")
    messages = relationship("Message", back_populates="character")
    chapters: Mapped[List["Chapter"]] = relationship(secondary=chapter_character_association, back_populates="characters") # type: ignore
    scenes: Mapped[List["Scene"]] = relationship(secondary=scene_character_association, back_populates="characters") # type: ignore