from sqlalchemy.orm import Session
from app.models.message import Message
from app.schemas import message as message_schema

def get_messages(db: Session):
    """Get all messages"""
    return db.query(Message).all()

def create_message(db: Session, message: message_schema.MessageCreate):
    db_message = Message(
        scene_id = message.scene_id,
        character_id = message.character_id,
        content = message.content,
        timestamp = message.timestamp
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message