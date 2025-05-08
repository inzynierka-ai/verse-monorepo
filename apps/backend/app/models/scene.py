from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.associations import scene_character_association

class Scene(Base):
    __tablename__ = 'scenes'
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    uuid = Column(String, nullable=False)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    status = Column(String, default="generation_not_started", nullable=False)


    # Relationships
    story = relationship("Story", back_populates="scenes")
    location = relationship("Location", back_populates="scenes")
    messages = relationship("Message", back_populates="scene")
    characters = relationship("Character", secondary=scene_character_association, back_populates="scenes")
    summary = relationship("SceneSummary", uselist=False, back_populates="scene")

class SceneSummary(Base):
    __tablename__ = 'scene_summaries'
    
    id = Column(Integer, primary_key=True, index=True)
    scene_id = Column(Integer, ForeignKey('scenes.id'), nullable=False, unique=True)
    total_messages = Column(Integer, nullable=False)
    character_participation = Column(JSON, nullable=False)
    key_events = Column(JSON, nullable=False)
    sentiment = Column(JSON, nullable=False)
    relationships = Column(JSON, nullable=False)
    
    # Relationships
    scene = relationship("Scene", back_populates="summary")