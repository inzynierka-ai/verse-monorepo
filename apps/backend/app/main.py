from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.routers.api import api_router
from app.db.session import engine, Base
from app.models import *
from app.db.seed import seed_database

app = FastAPI(title="Verse", description="Create your own story", version="0.1.0")
Base.metadata.create_all(bind=engine)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the aggregated router
app.include_router(api_router)

class ChatMessage(BaseModel):
    type: str
    content: str
    sceneId: str

@app.on_event("startup")
def startup_event():
    seed_database()

@app.get("/")
async def root():
    return {"message": "Welcome to My FastAPI App"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
