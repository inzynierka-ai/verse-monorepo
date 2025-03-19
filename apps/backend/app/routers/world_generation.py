from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.services.llm import LLMService
from app.schemas.schemas_ws import WorldGenerationRequest, ErrorMessage, WorldGenerationInput
from app.utils.websocket_manager import WorldGenWebSocketManager
from app.services.world_generation.world_generation_coordinator import WorldGenerationCoordinator

router = APIRouter(
    prefix="/world-generation",
    tags=["world-generation"],
)

# Create a singleton instance of the WebSocket manager
websocket_manager = WorldGenWebSocketManager()

def get_llm_service():
    return LLMService()

@router.websocket("/ws")
async def world_generation_websocket(
    websocket: WebSocket,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    WebSocket endpoint for world generation.
    
    This endpoint handles the entire world generation process in a streaming manner,
    sending updates to the client as each step completes.
    
    The generation flow follows these steps:
    1. World template generation
    2. Character and location generation (in parallel)
    3. Conflict generation
    4. World integration
    5. Narration
    
    Each step sends progress updates and completed data through the WebSocket.
    """
    coordinator = WorldGenerationCoordinator(websocket_manager, llm_service)
    
    async with websocket_manager.session(websocket) as session_id:
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                
                try:
                    # Parse the request
                    request = WorldGenerationRequest.model_validate_json(data)
                    
                    if request.type == "generate_world":
                        # Start world generation in background
                        # This will send updates through the WebSocket as generation progresses
                        await coordinator.generate_world(
                            session_id=session_id,
                            input_data=WorldGenerationInput(
                                world=request.world,
                                playerCharacter=request.playerCharacter
                            )
                        )
                except ValueError as e:
                    # Handle invalid request format
                    await websocket_manager.send_message(
                        session_id,
                        ErrorMessage(
                            type="error", 
                            message="Invalid request format",
                            details=str(e)
                        )
                    )
                
        except WebSocketDisconnect:
            # Client disconnected
            pass
        except Exception as e:
            # Unexpected error
            try:
                await websocket_manager.send_message(
                    session_id,
                    ErrorMessage(
                        type="error",
                        message="Unexpected error",
                        details=str(e)
                    )
                )
            except:
                pass 