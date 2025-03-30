import os
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.routers.api import api_router
from app.db.session import engine, Base
from app.models import *
from app.db.seed import seed_database
from app.core.config import settings
import os

app = FastAPI(title="Verse", description="Create your own story", version="0.1.0")
# Base.metadata.create_all(bind=engine)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, limit this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Mount media directory for serving generated images
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")


# Mount media directory for serving generated images
os.makedirs("./media", exist_ok=True)
app.mount("/media", StaticFiles(directory="./media"), name="media")

class ChatMessage(BaseModel):
    type: str
    content: str
    sceneId: str

# @app.on_event("startup")
# def startup_event():
#     # seed_database()
#     pass

@app.get("/")
def read_root():
    return {"message": "Welcome to Verse API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
