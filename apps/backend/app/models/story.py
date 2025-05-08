from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    brief_description = Column(Text, nullable=True)  # New column
    rules = Column(Text, nullable=False)
    uuid = Column(String, nullable=False, unique=True)
    
    user = relationship("User", back_populates="stories")
    locations = relationship("Location", back_populates="story")
    characters = relationship("Character", back_populates="story")
    scenes = relationship("Scene", back_populates="story")
