from sqlalchemy import Integer, Column, String, Text, DateTime, ARRAY, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.session import Base

class WorldEntity(Base):
    __tablename__ = "world_entities"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    name = Column(String, nullable=False)
    canonical_description = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    aliases = Column(ARRAY(String), default=[])
    discovered_in_scene = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    story = relationship("Story", back_populates="world_entities")