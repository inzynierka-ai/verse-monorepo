from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging

from app.schemas import message as message_schema

from app.db.session import get_db
from app.crud.messages import get_messages, create_message as create_message_service, get_messages_by_scene_and_character

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/", response_model=List[message_schema.Message])
async def list_messages(db: Session = Depends(get_db)):
    messages = get_messages(db)
    if not messages:
        raise HTTPException(status_code=404, detail=f"No messages found")
    return messages

@router.post("/", response_model=message_schema.Message)
async def create_message(message: message_schema.MessageCreate, db: Session = Depends(get_db)):
    return create_message_service(db, message)

@router.get("/scenes/{scene_uuid}/characters/{character_uuid}", response_model=List[message_schema.Message])
async def gets_messages_by_scene_and_character(scene_uuid: str, character_uuid: str, db: Session = Depends(get_db)):
    return get_messages_by_scene_and_character(db, scene_uuid, character_uuid)