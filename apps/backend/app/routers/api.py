from fastapi import APIRouter
from . import stories, chapters, scenes, messages, characters, locations, auth

from .game_ws import router as game_ws_router
from . import stories, chapters, scenes, messages, characters, locations, auth, comfyui

api_router = APIRouter()

# Existing routers
api_router.include_router(auth.router)
api_router.include_router(stories.router)
api_router.include_router(chapters.router)
api_router.include_router(scenes.router)
api_router.include_router(messages.router)
api_router.include_router(characters.router)
api_router.include_router(locations.router)
api_router.include_router(game_ws_router.router)
api_router.include_router(comfyui.router)

