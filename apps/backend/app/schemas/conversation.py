from typing import List, Dict, Any, Literal, Optional, Union
from pydantic import BaseModel

class ClientMessage(BaseModel):
    """Message sent from the client to the server"""
    sceneId: str
    characterId: str
    messages: List[Dict[str, Any]]  # List of previous messages for context

class ChatChunkMessage(BaseModel):
    """Chunk of a response from the character"""
    type: Literal["chat_chunk"]
    content: str

class ChatCompleteMessage(BaseModel):
    """Signal that the character's response is complete"""
    type: Literal["chat_complete"]

class ErrorMessage(BaseModel):
    """Error message sent to the client"""
    type: Literal["error"]
    content: str
    details: Optional[str] = None

# Union type for server messages
ServerMessage = Union[ChatChunkMessage, ChatCompleteMessage, ErrorMessage] 