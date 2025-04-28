from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.associations import scene_character_association

class Scene(Base):
    __tablename__ = 'scenes'
    
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    uuid = Column(String, nullable=False)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)


    # Relationships
    story = relationship("Story", back_populates="scenes")
    location = relationship("Location", back_populates="scenes")
    messages = relationship("Message", back_populates="scene")
    characters = relationship("Character", secondary=scene_character_association, back_populates="scenes")