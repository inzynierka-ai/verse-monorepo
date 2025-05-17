from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from app.services.image_generation.comfyui_service import ComfyUIService
from pydantic import BaseModel

router = APIRouter(prefix="/comfyui", tags=["comfyui"])

class ImageGenerationRequest(BaseModel):
    prompt: str
    context_type: str = "character"  # Default to character if not specified

class ImagePathsModel(BaseModel):
    base: str
    images: List[str]  # Adding images field as a list of paths

class ImageGenerationResponse(BaseModel):
    success: bool
    imagePath: str
    promptId: Optional[str] = None
    error: Optional[str] = None
    imagePaths: Optional[Dict[str, Any]] = None

class GenerationProgressResponse(BaseModel):
    promptId: str
    step: int
    totalSteps: int
    status: str

@router.post("/generate-image", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """Generate image using ComfyUI based on text prompt"""
    comfyui_service = ComfyUIService()
    try:
        result = comfyui_service.generate_image(request.prompt, request.context_type)
        return result
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=f"Generation timed out: {str(e)}")
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"ComfyUI service unavailable: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

