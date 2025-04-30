from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from typing import List
from sqlalchemy.orm import Mapped
from app.db.session import Base
from app.models.associations import location_character_association, location_connections

class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    image_prompt = Column(String)
    rules = Column(String) # rules for the location
    colors = Column(String) # interface colors
    image_dir = Column(String) # directory where all location images are stored
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    uuid = Column(String, nullable=False)
    
    # Relationships
    story = relationship("Story", back_populates="locations")
    scenes = relationship("Scene", back_populates="location")
    characters: Mapped[List["Character"]] = relationship(secondary=location_character_association, back_populates="locations") # type: ignore
    
    # Self-referential relationship for connected locations
    connected_locations: Mapped[List["Location"]] = relationship(
        "Location",
        secondary=location_connections,
        primaryjoin=(id == location_connections.c.from_location_id),
        secondaryjoin=(id == location_connections.c.to_location_id),
        backref="connected_from"
    )