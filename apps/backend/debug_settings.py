from pydantic_settings import BaseSettings
import os
import sys

# Display Pydantic version information
import pydantic
print(f"Pydantic version: {pydantic.__version__}")

# Display environment variables
print("Environment variables:")
for key, value in os.environ.items():
    print(f"  {key}: {value}")

# Simple class that accepts everything
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

sys.exit(0)  # Close process after debugging