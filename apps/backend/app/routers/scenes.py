from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from typing import List
from sqlalchemy.orm import Session

from app.schemas.scene import (Message,SceneMessage,SceneChatChunk,SceneAnalysisUpdate,SceneChatComplete)
from app.schemas.websocket import ErrorMessage
from app.services.scenes import SceneService
from app.crud.characters import get_character
from app.crud.locations import get_location
from app.db.session import get_db
from app.schemas import scene as scene_schema
from app.schemas import message as message_schema
from app.schemas import character as character_schema
from app.schemas import location as location_schema
from app.crud.scenes import get_scene, create_scene as create_scene_service
from app.services.auth import ResourcePermission, get_current_user
from app.schemas.user import User

# Create permission checker
scene_permission = ResourcePermission("scene")
chapter_permission = ResourcePermission("chapter")


router = APIRouter(
    prefix="/scenes",
    tags=["scenes"]
)

@router.get("/{scene_id}", response_model=scene_schema.Scene)
async def get_scene_id(scene = Depends(scene_permission), current_user: User = Depends(get_current_user)):
    """Get a specific scene that belongs to the current user"""
    return scene


@router.get("/{scene_id}/messages", response_model=List[message_schema.Message])
async def get_scene_messages(scene = Depends(scene_permission), current_user: User = Depends(get_current_user)):
    """Get all messages for a specific scene that belongs to the current user"""
    return scene.messages

@router.get("/{scene_id}/characters", response_model=List[character_schema.Character])
async def get_scene_characters(scene = Depends(scene_permission), current_user: User = Depends(get_current_user)):
    """Get all characters for a specific scene that belongs to the current user"""
    return scene.characters

@router.get("/{scene_id}/location", response_model=location_schema.Location)
async def get_scene_location(scene = Depends(scene_permission), current_user: User = Depends(get_current_user)):
    """Get the location for a specific scene that belongs to the current user"""
    return scene.location

@router.post("/", response_model=scene_schema.Scene)
def create_scene(
    scene: scene_schema.SceneCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new scene"""
    chapter = Depends(chapter_permission)(scene.chapter_id, db, current_user)
    return create_scene_service(db, scene)

@router.websocket("/{scene_id}")
async def scene_websocket(websocket: WebSocket, scene_id: str, db: Session = Depends(get_db)):
    scene_service = SceneService()
    character = get_character(db, character_id=1)  # For now, hardcoded to character_id 1 (Alistair)
    location = get_location(db, location_id=1)     # For now, hardcoded to location_id 1
    
    if not character or not location:
        raise HTTPException(status_code=404, detail="Character or location not found")
    
    try:
        system_prompt = await scene_service.load_character_prompt(character.id, location.id)
    except ValueError as e:
        print(f"Error loading character prompt: {str(e)}")
        await websocket.close()
        return
    
    async with scene_service.manage_websocket(websocket):
        try:
            while True:
                raw_message = await websocket.receive_text()
                try:
                    message = SceneMessage.model_validate_json(raw_message)
                except Exception as e:
                    error = ErrorMessage(type="error", content="Invalid message format")
                    await websocket.send_text(error.model_dump_json())
                    continue

                if not scene_service.verify_scene_id(message.sceneId, scene_id):
                    error = ErrorMessage(type="error", content="Scene ID mismatch")
                    await websocket.send_text(error.model_dump_json())
                    continue

                async for chunk in await scene_service.process_message(message, system_prompt):
                    chunk_message = SceneChatChunk(
                        type="chat_chunk",
                        content=chunk
                    )
                    await websocket.send_text(chunk_message.model_dump_json())

                complete_message = SceneChatComplete(type="chat_complete")
                await websocket.send_text(complete_message.model_dump_json())

                analysis = scene_service.get_character_analysis(character.id)
                analysis_message = SceneAnalysisUpdate(
                    type="analysis",
                    analysis=analysis
                )
                await websocket.send_text(analysis_message.model_dump_json())

        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"Error in websocket connection: {str(e)}")
            await websocket.close() 