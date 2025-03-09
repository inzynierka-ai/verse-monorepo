import asyncio
import json
from app.services.world_generation.location_generator import generate_locations
from app.schemas.world_wizard import (
    LocationGeneratorInput, 
    LocationTemplate, 
    SettingInfo
)

async def test_location_generator():
    # Create input data
    input_data = LocationGeneratorInput(
        world_setting=SettingInfo(
            theme="Cyberpunk dystopia",
            atmosphere="Gritty and oppressive",
            description="A futuristic megacity where corporations rule and technology has advanced but society has regressed."
        ),
        basic_locations=[
            LocationTemplate(
                id="loc1",
                name="Neon District",
                brief="A bustling area full of bright neon signs and street vendors."
            ),
            LocationTemplate(
                id="loc2",
                name="Corporate Plaza",
                brief="A sterile, heavily monitored area where the corporate elites conduct business."
            )
        ]
    )
    
    try:
        # Call the function
        result = await generate_locations(input_data)
        
        # Print the result
        print("Success! Generated locations:")
        print(json.dumps(result.model_dump(), indent=2))
        return result
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(test_location_generator()) 