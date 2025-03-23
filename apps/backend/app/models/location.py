from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from typing import List
from sqlalchemy.orm import Mapped
from app.db.session import Base
from app.models.associations import chapter_location_association 

class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image_prompt = Column(String, nullable=True)
    details = Column(String, nullable=False) # incl. connected loacations, rules
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    
    story = relationship("Story", back_populates="locations")
    scenes = relationship("Scene", back_populates="location")
    chapters: Mapped[List["Chapter"]] = relationship(secondary=chapter_location_association, back_populates="locations") # type: ignore
    