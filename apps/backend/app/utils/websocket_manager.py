from fastapi import WebSocket
from typing import Dict, Any, Optional, AsyncGenerator
from contextlib import asynccontextmanager
import json
import uuid

from app.schemas.schemas_ws import ServerMessage

class WorldGenWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket) -> str:
        """Accept connection and return a session ID"""
        session_id = str(uuid.uuid4())
        await websocket.accept()
        self.active_connections[session_id] = websocket
        return session_id
        
    def disconnect(self, session_id: str):
        """Remove connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    @asynccontextmanager
    async def session(self, websocket: WebSocket):
        """Context manager for WebSocket session"""
        session_id = await self.connect(websocket)
        try:
            yield session_id
        finally:
            self.disconnect(session_id)
    
    async def send_message(self, session_id: str, message: ServerMessage):
        """Send a message to a specific client"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(message.model_dump_json())
            except Exception as e:
                print(f"Error sending message: {str(e)}")
                self.disconnect(session_id) 