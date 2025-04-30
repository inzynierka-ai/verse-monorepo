from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Story(Base):
    __tablename__ = 'stories'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String)
    description = Column(String)
    rules = Column(String)
    uuid = Column(String, nullable=False)
    
    user = relationship("User", back_populates="stories")
    locations = relationship("Location", back_populates="story")
    characters = relationship("Character", back_populates="story")
    scenes = relationship("Scene", back_populates="story")
