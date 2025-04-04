import asyncio
import json
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, backend_dir)

from app.services.game_engine.tools.location_generator import LocationGenerator
from app.schemas.world_generation import World
from app.services.llm import LLMService

async def main():
    # Create example data
    world = World(
        description="A cyberpunk world set in 2077, where corporations control society and cybernetic enhancements are common.",
        rules=["Characters should have cybernetic enhancements.", 
               "The world is divided between corporate elites and struggling lower classes.",
               "Technology is advanced but unevenly distributed."]
    )
    
    # Initialize services
    llm_service = LLMService()
    location_generator = LocationGenerator(llm_service)
    
    # Generate location
    print("Generating location...")
    location = await location_generator.generate_location(world)
    
    # Save to JSON file
    output_path = Path(__file__).parent / "generated_location.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(location.model_dump(), f, indent=2)
    
    print(f"Location generated and saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main()) 