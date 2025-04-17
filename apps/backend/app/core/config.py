import os
from typing import List, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Simple settings loader that gets values directly from environment variables."""
    
    # API settings
    PROJECT_NAME = "Verse"
    BACKEND_URL: Optional[str] = os.getenv("BACKEND_URL")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv("BACKEND_CORS_ORIGINS", "").split(",") if origin.strip()
    ]
    
    # Security settings
    SECRET_KEY: Optional[str] = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "0"))
    
    # Media settings
    MEDIA_ROOT = os.path.join(os.getcwd(), "media")
    
    # Database settings
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Frontend URL
    FRONTEND_URL: Optional[str] = os.getenv("FRONTEND_URL")
    
    # LLM settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE: Optional[str] = os.getenv("OPENAI_API_BASE")
    OPEN_ROUTER_API_KEY: Optional[str] = os.getenv("OPEN_ROUTER_API_KEY")
    OPEN_ROUTER_API_BASE: Optional[str] = os.getenv("OPEN_ROUTER_API_BASE")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Langfuse settings
    LANGFUSE_SECRET_KEY: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_PUBLIC_KEY: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_HOST: Optional[str] = os.getenv("LANGFUSE_HOST")
    
    # ComfyUI settings
    COMFYUI_API_URL: Optional[str] = os.getenv("COMFYUI_API_URL")
    COMFYUI_WORKFLOWS_DIR: str = str(Path(os.getcwd()) / "comfyui_workflows")


# Create global settings instance
settings = Settings()
