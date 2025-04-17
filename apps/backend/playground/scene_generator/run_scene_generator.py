import asyncio
import json
import uuid
from typing import List, Dict, Any
import logging
from pathlib import Path
from app.services.scene_generator import SceneGeneratorAgent
from app.services.llm import LLMService
from app.schemas.story_generation import Story, Location, Character, Scene

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create sample data
async def create_sample_data() -> Dict[str, Any]:
    """Create sample data for testing the SceneGeneratorAgent"""
    
    # Create LLM service
    llm_service = LLMService()
    
    # Create a sample story
    story = Story(
        id=1,
        title="Enchanted Realms",
        description="A fantasy adventure where magic has returned to the world after centuries of absence, causing chaos and wonder.",
        rules=[],
        user_id=1,
        uuid=str(uuid.uuid4())
    )
    
    # Create a player character
    player = Character(
        name="Elara Windwhisper",
        role="player",
        description="A young elven mage with flowing silver hair and bright amber eyes that seem to glow in the dark.",
        backstory="Born with a natural affinity for arcane energies, Elara has spent her life studying the ancient texts of magic. When spells suddenly began working again, she left her secluded tower to explore the transformed world.",
        uuid=str(uuid.uuid4()),
        personalityTraits=["curious", "intelligent", "somewhat arrogant"],
        goals=["Discover the source of magic's return", "Learn rare spells"],
        relationships=[],
        imageUrl=""
    )
    
    # Create a list of characters
    characters: List[Character] = []
    
    # Create a list of locations
    locations: List[Location] = [
        
    ]

    previous_scene = None

    return {
        "llm_service": llm_service,
        "story": story,
        "player": player,
        "characters": characters,
        "locations": locations,
        "previous_scene": previous_scene
    }

async def main():
    # Create sample data
    logger.info("Creating sample data...")
    sample_data = await create_sample_data()
    
    # Initialize the SceneGeneratorAgent
    logger.info("Initializing SceneGeneratorAgent...")
    scene_generator = SceneGeneratorAgent(
        llm_service=sample_data["llm_service"],
        story=sample_data["story"],
        player=sample_data["player"]
    )

    # Generate a scene
    logger.info("Generating scene...")
    generated_scene = await scene_generator.generate_scene(
        characters=sample_data["characters"],
        locations=sample_data["locations"],
        previous_scene=sample_data["previous_scene"]
    )
    
    # Create results directory if it doesn't exist
    output_file = Path(__file__).parent / f"generated_scenes/{sample_data['story'].uuid}.json"
    
    # Save the generated scene to a JSON file
    logger.info(f"Saving generated scene to {output_file}...")
    
    with open(output_file, "w") as f:
        json.dump(generated_scene, f, indent=2)
    
    # Print a summary of the generated scene
    logger.info("Scene generation complete!")
    logger.info(f"Location: {generated_scene['location']['name']}")
    logger.info(f"Characters: {[char['name'] for char in generated_scene['characters']]}")
    logger.info(f"Description length: {len(generated_scene['description'])} characters")
    logger.info(f"Full output saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main()) 