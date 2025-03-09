from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.db.session import Base

class Story(Base):
    __tablename__ = 'stories'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    # date_created = Column(TIMESTAMP(timezone=True), server_default=func.now())
    # date_last_played = Column(TIMESTAMP(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="stories")
    chapters = relationship("Chapter", back_populates="story")
    locations = relationship("Location", back_populates="story")
    characters = relationship("Character", back_populates="story")
