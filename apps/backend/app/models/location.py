from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

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