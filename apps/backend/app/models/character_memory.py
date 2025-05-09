from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.session import Base  # Fix this import to match character.py

class CharacterMemory(Base):
    __tablename__ = "character_memories"

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=False)
    memory_text = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    uuid = Column(Text, unique=True, nullable=False)

    character = relationship("Character", back_populates="memories")
    scene = relationship("Scene")