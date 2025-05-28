from pydantic import BaseModel


class ImageGenerationRequest(BaseModel):
    prompt: str


class ImagePathsModel(BaseModel):
    base: str


class ImageGenerationResponse(BaseModel):
    imagePaths: ImagePathsModel
