from fastapi import APIRouter
from . import stories, chapters, scenes, messages, characters, locations, auth

from .game_ws import router as game_ws_router
from . import stories, chapters, scenes, messages, characters, locations, auth, comfyui

api_router = APIRouter()

# Istniejące routery
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
api_router.include_router(chapters.router, prefix="/api")
api_router.include_router(scenes.router, prefix="/api")
api_router.include_router(messages.router, prefix="/api")
api_router.include_router(characters.router, prefix="/api")
api_router.include_router(locations.router, prefix="/api")
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(game_ws_router.router)
# Dodaj router ComfyUI
api_router.include_router(comfyui.router, prefix="/comfyui", tags=["comfyui"])
# api_router.include_router(world_wizard_router, prefix="/api")  # Tymczasowo wyłączone
