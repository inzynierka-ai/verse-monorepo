from typing import List
from sqlalchemy.orm import Session
from app.models.message import Message
from app.schemas import message as message_schema
from app.crud.characters import get_character_by_uuid
from app.crud.scenes import get_scene_by_uuid

def get_messages(db: Session):
    """Get all messages"""
    return db.query(Message).all()

def get_messages_by_scene(db: Session, scene_uuid: str):
    """Get messages by scene"""
    scene = get_scene_by_uuid(db, scene_uuid)
    if not scene:
        empty_list: List[Message] = []
        return empty_list
    return db.query(Message).filter(Message.scene_id == scene.id).order_by(Message.id).all()

def create_message(db: Session, message: message_schema.MessageCreate):
    db_message = Message(
        scene_id = message.scene_id,
        character_id = message.character_id,
        content = message.content,
        role = message.role,
        timestamp = message.timestamp,
        uuid = message.uuid
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_by_scene_and_character(db: Session, scene_uuid: str, character_uuid: str):
    """Get messages by scene and character"""
    scene = get_scene_by_uuid(db, scene_uuid)
    character = get_character_by_uuid(db, character_uuid)
    if not scene or not character:
        empty_list: List[Message] = []
        return empty_list
    return db.query(Message).filter(Message.scene_id == scene.id, Message.character_id == character.id).order_by(Message.id).all()