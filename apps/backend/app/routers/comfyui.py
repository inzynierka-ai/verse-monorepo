from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.services.comfyui_service import ComfyUIService
from pydantic import BaseModel

router = APIRouter(tags=["comfyui"])

class ImageGenerationRequest(BaseModel):
    prompt: str

class ImagePathsModel(BaseModel):
    base: str
    images: List[str]  # Adding images field as a list of paths

class ImageGenerationResponse(BaseModel):
    imagePaths: ImagePathsModel

@router.post("/generate-image", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """Generate image using ComfyUI based on text prompt"""
    comfyui_service = ComfyUIService()
    try:
        result = await comfyui_service.generate_image_from_prompt(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))