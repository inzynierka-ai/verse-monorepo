from typing import List, Literal
from pydantic import BaseModel, ConfigDict
from app.schemas.websocket import BaseClientMessage, BaseServerMessage

from pydantic import BaseModel
from app.schemas.message import Message
from app.schemas.character import Character
from app.schemas.location import Location
class Scene(BaseModel):
    id: int
    description: str
    location_id: int
    story_id: int
    uuid: str
    location: Location
    characters: List[Character]
    messages: List[Message]
    description: str

    model_config = ConfigDict(from_attributes=True)

class SceneClientMessage(BaseClientMessage):
    """Base class for all scene-related client messages"""
    type: str
    sceneId: str

class SceneMessage(SceneClientMessage):
    """Message sent by client to interact with scene"""
    type: Literal["message"]
    content: str

class AvailableAction(BaseModel):
    name: str

class SceneAnalysis(BaseModel):
    relationshipLevel: float
    availableActions: List[AvailableAction]

class SceneServerMessage(BaseServerMessage):
    """Base class for all scene-related server messages"""
    type: str

class SceneChatChunk(SceneServerMessage):
    type: Literal["chat_chunk"]
    content: str

class SceneAnalysisUpdate(SceneServerMessage):
    type: Literal["analysis"]
    analysis: SceneAnalysis

class SceneChatComplete(SceneServerMessage):
    type: Literal["chat_complete"]

# Union type for all possible scene server messages
SceneServerMessageUnion = SceneChatChunk | SceneAnalysisUpdate | SceneChatComplete 

class Message(BaseModel):
    id: str
    content: str
    character_id: str
    scene_id: str
    timestamp: str