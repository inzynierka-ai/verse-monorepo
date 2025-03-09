import asyncio
import json
from app.services.world_generation.conflict_generator import generate_conflict
from app.schemas.world_wizard import (
    ConflictGeneratorInput,
    SettingInfo,
    ConflictTemplate
)

async def test_conflict_generator():
    # Create input data
    input_data = ConflictGeneratorInput(
        world_setting=SettingInfo(
            theme="Cyberpunk dystopia",
            atmosphere="Gritty and oppressive",
            description="A futuristic megacity where corporations rule and technology has advanced but society has regressed."
        ),
        initial_conflict=ConflictTemplate(
            description="A mysterious hacker has discovered a way to manipulate corporate security systems, threatening the power structure."
        ),
        character_summaries=[
            {
                "id": "char1",
                "name": "Max Reynolds",
                "role": "Hacker",
                "description": "A skilled computer specialist who can break through any security system."
            },
            {
                "id": "char2",
                "name": "Victoria Chen",
                "role": "Corporate Executive",
                "description": "A ruthless executive who will protect corporate interests at any cost."
            }
        ],
        locations=[
            {
                "id": "loc1",
                "name": "Neon District",
                "description": "A bustling area full of bright neon signs and street vendors."
            },
            {
                "id": "loc2",
                "name": "Corporate Plaza",
                "description": "A sterile, heavily monitored area where the corporate elites conduct business."
            }
        ]
    )
    
    try:
        # Call the function
        result = await generate_conflict(input_data)
        
        # Print the result
        print("Success! Generated conflict:")
        print(json.dumps(result.model_dump(), indent=2))
        return result
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(test_conflict_generator()) 