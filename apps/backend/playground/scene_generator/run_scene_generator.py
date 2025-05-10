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
        image_dir=""
    )
    
    # Create a list of characters
    characters: List[Character] = [
        Character(
            name="Thorin Ironheart",
            role="npc",
            description="A gruff dwarven blacksmith with a thick beard adorned with metal trinkets. His arms are covered in magical runes.",
            backstory="Once a simple smith, Thorin discovered he could infuse his creations with magical properties when the arcane energies returned. Now he crafts enchanted weapons for adventurers.",
            uuid=str(uuid.uuid4()),
            personalityTraits=["stubborn", "loyal", "perfectionist"],
            goals=["Create the most powerful enchanted weapon in the realm"],
            relationships=[],
            image_dir=""
        ),
        Character(
            name="Sylvia Nightshade",
            role="npc",
            description="A mysterious human woman dressed in dark robes with purple accents. Her eyes are deep black and seem to hold ancient secrets.",
            backstory="Leader of the Shadow Conclave, a group that believes magic's return is a curse rather than a blessing. Secretly affected by wild magic that's slowly transforming her.",
            uuid=str(uuid.uuid4()),
            personalityTraits=["secretive", "calculating", "protective"],
            goals=["Find a way to control wild magic", "Protect common folk from magical dangers"],
            relationships=[],
            image_dir=""
        ),
        Character(
            name="Zephyr",
            role="npc",
            description="A small air elemental that appears as a swirling vortex of wind and light. Often changes shape and size depending on mood.",
            backstory="Born when magic returned to the world, Zephyr is a young elemental still learning about its existence. Follows Elara out of curiosity and friendship.",
            uuid=str(uuid.uuid4()),
            personalityTraits=["playful", "fickle", "loyal"],
            goals=["Experience everything the material world has to offer"],
            relationships=[],
            image_dir=""
        )
    ]
    
    # Create a list of locations
    locations: List[Location] = [
        Location(
            name="Crystalspire Tower",
            description="A tall, translucent tower made of crystalline material that changes color with the time of day. Home to various mages studying the return of magic.",
            uuid=str(uuid.uuid4()),
            rules=["Magic is amplified within these walls", "All visitors must register with the tower guardian"],
            image_dir="",
            id=1
        ),
        Location(
            name="Ironforge Market",
            description="A bustling dwarven marketplace filled with stalls selling enchanted items. The air is thick with smoke from forges and the smell of magical reagents.",
            uuid=str(uuid.uuid4()),
            rules=["All trades must be witnessed by a market official", "No casting offensive spells"],
            image_dir="",
            id=2
        ),
        Location(
            name="Whispering Woods",
            description="A dense forest where the trees seem to communicate with each other. Magical creatures have taken residence here, and strange lights can be seen at night.",
            uuid=str(uuid.uuid4()),
            rules=["Don't harm the trees", "Beware of will-o'-wisps after dark"],
            image_dir="",
            id=3
        ),
        Location(
            name="Shadow Conclave Hideout",
            description="A hidden underground complex where the Shadow Conclave operates. Warded against magical detection and filled with artifacts that suppress arcane energies.",
            uuid=str(uuid.uuid4()),
            rules=["Speak only in whispers", "All magic must be approved by Sylvia"],
            image_dir="",
            id=4
        )
    ]

    previous_scene = Scene(
        location=locations[0],
        characters=characters,
        description="The players are in the Crystalspire Tower, discussing the return of magic.",
        summary="The players were in the Crystalspire Tower, discussing the return of magic. Elara was able to cast a spell to create a portal to the Ironforge Market."
    )

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
    logger.info(f"Location: {generated_scene.location.name}")
    logger.info(f"Characters: {[char.name for char in generated_scene.characters]}")
    logger.info(f"Description length: {len(generated_scene.description)} characters")
    logger.info(f"Full output saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main()) 