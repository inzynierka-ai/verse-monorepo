import asyncio
import os
import sys

# Add the project root to the path to ensure imports work correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from app.services.game_engine.tools.story_generator import StoryGenerator
from app.schemas.story_generation import StoryInput
from app.services.llm import LLMService

async def main():
    # Initialize services
    llm_service = LLMService()
    story_generator = StoryGenerator(llm_service=llm_service, db_session=None)
    
    # Sample story inputs
    sample_stories = [
        StoryInput(
            theme="Space exploration",
            genre="Science Fiction",
            year="2250",
            setting="Interstellar colony ship"
        ),
    ]
    
    # Generate a story using the first sample input
    user_id = 1  # Placeholder user ID for testing
    story = await story_generator.generate_story(user_id, sample_stories[0])
    
    # Print the generated story details
    print("\n=== GENERATED STORY ===")
    print(f"Title: {story.title}")
    print(f"Brief Description: {story.brief_description}")
    print("\nFull Description:")
    print(story.description)
    print("\nRules:")
    for i, rule in enumerate(story.rules, 1):
        print(f"{i}. {rule}")
    print(f"\nStory UUID: {story.uuid}")

if __name__ == "__main__":
    asyncio.run(main())

    # To try different sample inputs, change the index in sample_stories[0] to 1 or 2