from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from typing import List
from app.db.session import Base
from app.models.associations import chapter_character_association, chapter_location_association

class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    prompt = Column(String, nullable=False)

    # Relationships
    story = relationship("Story", back_populates="chapters")
    scenes = relationship("Scene", back_populates="chapter")
    locations: Mapped[List["Location"]] = relationship(secondary=chapter_location_association, back_populates="chapters") # type: ignore
    characters: Mapped[List["Character"]] = relationship(secondary=chapter_character_association, back_populates="chapters") # type: ignore