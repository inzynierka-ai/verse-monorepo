from pydantic_settings import BaseSettings
import os
import sys

# Wyświetl info o wersji pydantic
import pydantic
print(f"Pydantic version: {pydantic.__version__}")

# Wyświetl zmienne środowiskowe
print("Environment variables:")
for key, value in os.environ.items():
    print(f"  {key}: {value}")

# Prosta klasa która akceptuje wszystko
class DebugSettings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }

try:
    settings = DebugSettings()
    print("Settings loaded successfully!")
    print(settings.model_dump())
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

sys.exit(0)  # Zamknij proces po debugowaniu