from typing import List, Literal
from pydantic import BaseModel

class ClientMessage(BaseModel):
    type: Literal["message"]
    content: str
    sceneId: str

class AvailableAction(BaseModel):
    name: str

class SceneAnalysis(BaseModel):
    relationshipLevel: float
    availableActions: List[AvailableAction]

class ServerMessageBase(BaseModel):
    type: Literal["chat_chunk", "analysis", "chat_complete"]

class ChatChunkMessage(ServerMessageBase):
    type: Literal["chat_chunk"]
    content: str

class AnalysisMessage(ServerMessageBase):
    type: Literal["analysis"]
    analysis: SceneAnalysis

class ChatCompleteMessage(ServerMessageBase):
    type: Literal["chat_complete"]

ServerMessage = ChatChunkMessage | AnalysisMessage | ChatCompleteMessage 