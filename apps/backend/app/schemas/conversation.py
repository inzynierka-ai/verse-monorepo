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

class ModerationResult(BaseModel):
    """Result of content moderation"""
    is_flagged: bool
    violated_categories: Optional[Dict[str, bool]] = None
    processing_time_ms: Optional[float] = None

class EntityExtractionResult(BaseModel):
    """Result of entity extraction for vector search"""
    extracted_entities: List[str]
    processing_time_ms: Optional[float] = None

class VectorSearchResult(BaseModel):
    """Result of vector database search"""
    entities_found: List[Dict[str, Any]]  # List of entities with scores
    memories_found: List[Dict[str, Any]]  # List of memories with scores
    name_matches: int
    description_matches: int  
    vector_matches: int
    total_results: int
    processing_time_ms: Optional[float] = None

class ProcessingStatusMessage(BaseModel):
    """Status update message during message processing"""
    type: Literal["processing_status"]
    step: Literal["moderating", "extracting_entities", "searching_vectors", "building_prompt", "generating_response"]
    message: str
    debug_info: Optional[Union[ModerationResult, EntityExtractionResult, VectorSearchResult, Dict[str, Any]]] = None

class ConversationTopic(BaseModel):
    """A conversation topic with a short title and full message"""
    title: str  # Short 2-3 word title
    message: str  # Full message to send when clicked

class ConversationTopicsResponse(BaseModel):
    """Response containing conversation topic suggestions"""
    topics: List[ConversationTopic]

# Union type for server messages
ServerMessage = Union[ChatChunkMessage, ChatCompleteMessage, ErrorMessage, ProcessingStatusMessage]