from fastapi import APIRouter
from . import stories, chapters, scenes, messages, characters, locations, auth

from .game_ws import router as game_ws_router

# Create the main api router
api_router = APIRouter()

api_router.include_router(stories.router, prefix="/api") 
api_router.include_router(chapters.router, prefix="/api")
api_router.include_router(scenes.router, prefix="/api")
api_router.include_router(messages.router, prefix="/api")
api_router.include_router(characters.router, prefix="/api")
api_router.include_router(locations.router, prefix="/api")
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(game_ws_router.router)
