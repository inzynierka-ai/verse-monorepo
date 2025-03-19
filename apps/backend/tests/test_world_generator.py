import asyncio
import json
import sys
from app.schemas.world_generation import WorldSettings
from app.services.world_generation.world_generator import generate_complete_world


async def test_world_generator():
    """
    Test the complete world generation pipeline using the new world_generator module.
    """
    # Get user input or use defaults
    if len(sys.argv) > 1:
        description = sys.argv[1]
    else:
        description = "A remote space station where strange phenomena are occurring, causing tension among the crew."
    
    if len(sys.argv) > 2:
        additional_context = sys.argv[2]
    else:
        additional_context = None
    
    print(f"Starting complete world generation with description: {description}")
    if additional_context:
        print(f"Additional context: {additional_context}")
    
    # Create world settings
    settings = WorldSettings(
        description=description,
        additional_context=additional_context
    )
    
    # Generate the complete world
    try:
        print("\n=== GENERATING COMPLETE WORLD ===")
        world_data = await generate_complete_world(settings)
        
        # Print summary
        print("\n=== GENERATION COMPLETE ===")
        print(f"Setting summary: {world_data['setting']['summary'][:150]}...")
        print(f"Characters: {len(world_data['characters'])}")
        print(f"Locations: {len(world_data['locations'])}")
        print(f"Conflict: {world_data['conflict']['title']}")
        print(f"Story hooks: {len(world_data['story_hooks'])}")
        print(f"World rules: {len(world_data['world_rules'])}")
        
        # Save the output to a file
        with open("complete_world_output.json", "w") as f:
            json.dump(world_data, f, indent=2)
        
        print("\nComplete output saved to complete_world_output.json")
    
    except Exception as e:
        print(f"Error during world generation: {str(e)}")
        raise e


if __name__ == "__main__":
    asyncio.run(test_world_generator()) 