from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
