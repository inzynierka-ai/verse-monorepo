import asyncio
import json
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.world_generation import (
    CharacterGenerator, 
    CharacterGeneratorInput,
    SettingInfo,
    CharacterTemplate
)

async def test_character_generator():
    """Test the Character Generator agent."""
    
    # Create input data
    input_data = CharacterGeneratorInput(
        world_setting=SettingInfo(
            theme="Small town with dark secrets",
            atmosphere="Eerie and mysterious",
            description="A secluded small town surrounded by dense forests. The town appears idyllic on the surface, but harbors dark secrets and strange phenomena that the residents either ignore or actively hide."
        ),
        basic_characters=[
            CharacterTemplate(
                id="char1",
                name="Sheriff Brody",
                role="Town Sheriff",
                brief="The dedicated town sheriff who maintains order while hiding his suspicions about strange events",
                appearance_hint="Middle-aged man with weathered face and constant tired expression"
            ),
            CharacterTemplate(
                id="char2",
                name="Sarah Miller",
                role="Newcomer",
                brief="A journalist who recently moved to town to investigate rumors of strange occurrences",
                appearance_hint="Young woman with sharp eyes and a notebook always in hand"
            ),
            CharacterTemplate(
                id="char3",
                name="Old Man Jenkins",
                role="Town Elder",
                brief="The oldest resident who knows more about the town's history than anyone else",
                appearance_hint="Elderly man with piercing blue eyes and a walking cane"
            )
        ]
    )
    
    # Create Character Generator instance
    generator = CharacterGenerator()
    
    # Process the input
    try:
        output = await generator.process(input_data)
        
        # Print the results
        print("\n=== Character Generator Results ===\n")
        for character in output.detailed_characters:
            print(f"Character: {character.name} ({character.role})")
            print(f"Description: {character.description[:100]}...")
            print("Personality Traits:")
            for trait in character.personality_traits:
                print(f"  - {trait.name}: {trait.description[:50]}...")
            print(f"Backstory: {character.backstory[:100]}...")
            print(f"Goals: {', '.join(character.goals)}")
            print(f"Appearance: {character.appearance[:100]}...")
            print("\n" + "-"*50 + "\n")
        
        # Save the full results to a file
        with open("character_generator_output.json", "w") as f:
            f.write(json.dumps(output.dict(), indent=2))
        print(f"Full results saved to character_generator_output.json")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_character_generator()) 