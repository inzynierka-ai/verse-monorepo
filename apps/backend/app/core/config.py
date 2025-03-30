from pydantic_settings import BaseSettings
import os
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # Pola z nazwami dokładnie jak w zmiennych środowiskowych (małe litery)
    database_url: str = "postgresql://postgres:postgres@db:5432/verse"
    frontend_url: str = "http://localhost:5173"
    openai_api_base: Optional[str] = None
    
    # ComfyUI settings
    COMFYUI_API_URL: str = "http://host.docker.internal:8188"  # Użyj nazwy usługi z docker-compose
    COMFYUI_WORKFLOWS_DIR: str = str(Path(os.getcwd()) / "comfyui_workflows")
    
    # Dodaj ścieżki do domyślnego katalogu wyjściowego ComfyUI - zmienione na ścieżkę w kontenerze
    COMFYUI_DEFAULT_OUTPUT_DIR: str = "/app/comfyui_output"
    
    # Media settings
    MEDIA_ROOT: str = str(Path(os.getcwd()) / "media")
    MEDIA_URL: str = "/media/"
    
    model_config = {
        "env_file": ".env",
        "extra": "allow",
        "case_sensitive": False
    }

settings = Settings()
