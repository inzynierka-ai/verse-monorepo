from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    scene_id: int
    character_id: int
    content: str
    timestamp: datetime
    uuid: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int

    class Config:
        from_attributes = True
