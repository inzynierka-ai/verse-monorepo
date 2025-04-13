import logging

from app.db.seed import seed_database

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routers.api import api_router
from app.core.config import settings


app = FastAPI(title=settings.PROJECT_NAME, description="Create your own story", version="0.1.0", redirect_slashes=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Mount media directory for serving generated images
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
app.mount(settings.MEDIA_ROOT, StaticFiles(directory=settings.MEDIA_ROOT), name="media")

@app.on_event("startup")
def startup_event():
    seed_database()
    pass


@app.get("/")
def read_root():
    return {"message": "Welcome to Verse API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
