from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    scene_id = Column(Integer, ForeignKey('scenes.id'), nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP(), server_default=func.now())

    # Relationships
    scene = relationship("Scene", back_populates="messages")  
    character = relationship("Character", back_populates="messages")  