from pydantic import BaseModel
from typing import Dict, Any

class ImageGenerationRequest(BaseModel):
    prompt: str

class ImagePathsModel(BaseModel):
    base: str

class ImageGenerationResponse(BaseModel):
    imagePaths: ImagePathsModel