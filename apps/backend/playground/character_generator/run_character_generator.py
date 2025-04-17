import asyncio
import json
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, backend_dir)

from app.services.game_engine.tools.character_generator import CharacterGenerator
from app.schemas.story_generation import CharacterDraft, Story
from app.services.llm import LLMService

async def main():
    # Create example data
    story = Story(
        description="A cyberpunk story set in 2077, where corporations control society and cybernetic enhancements are common.",
        rules=["Characters should have cybernetic enhancements.", 
               "The story is divided between corporate elites and struggling lower classes.",
               "Technology is advanced but unevenly distributed."],
        title="Cyberpunk City"
    )
    
    character_draft = CharacterDraft(
        name="Raven",
        age=28,
        appearance="Tall, lean build with jet-black hair and cybernetic eye implants that glow blue.",
        background="Former corporate security specialist who turned against the system after discovering corruption."
    )
    
    # Initialize services
    llm_service = LLMService()
    character_generator = CharacterGenerator(llm_service)
    
    # Generate character
    print("Generating character...")
    character = await character_generator.generate_character(character_draft, story, is_player=True)
    
    # Save to JSON file
    output_path = Path(__file__).parent / "generated_character.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(character.model_dump(), f, indent=2)
    
    print(f"Character generated and saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main()) 