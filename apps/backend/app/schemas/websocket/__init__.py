from typing import Literal
from pydantic import BaseModel

class ErrorMessage(BaseModel):
    type: Literal["error"]
    content: str

class BaseClientMessage(BaseModel):
    """Base class for all client -> server messages"""
    pass

class BaseServerMessage(BaseModel):
    """Base class for all server -> client messages"""
    pass 