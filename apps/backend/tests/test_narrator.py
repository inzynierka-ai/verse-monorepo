import json
import os
import sys
import asyncio
from pprint import pprint

# Add the parent directory to path to allow importing the narrator module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from app.services.world_generation.narrator import Narrator
from app.services.llm import LLMService

async def main():
    """Test the Narrator module with example world data."""
    # Path to the example file - adjust if needed
    example_file = "complete_world_output.json"
    
    # Check if file exists
    if not os.path.exists(example_file):
        print(f"Error: Example file {example_file} not found.")
        print("Make sure you're running this script from the correct directory.")
        return
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Create narrator from file
    print(f"Creating narrator from example file: {example_file}")
    with open(example_file, 'r') as f:
        world_data = json.load(f)
    narrator = Narrator(world_data, llm_service)
    
    # Test both methods
    await test_template_based(narrator)
    await test_llm_based(narrator)

async def test_template_based(narrator):
    """Test template-based introduction generation."""
    print("\nGenerating template-based introduction...\n")
    introduction = await narrator.generate_introduction(use_llm=False)
    
    # Display the results
    print("=" * 80)
    print("TEMPLATE-BASED INTRODUCTION")
    print("=" * 80)
    
    for i, step in enumerate(introduction, 1):
        print(f"\nSTEP {i}: {step['title']}")
        print("-" * 50)
        print(step['content'])
    
    print("\n" + "=" * 80)
    print("END OF TEMPLATE-BASED INTRODUCTION")
    print("=" * 80)

async def test_llm_based(narrator):
    """Test LLM-based introduction generation."""
    print("\nGenerating LLM-enhanced introduction...\n")
    print("(This may take a moment as it calls the LLM API for each step)")
    
    try:
        introduction = await narrator.generate_introduction(use_llm=True)
        
        # Display the results
        print("=" * 80)
        print("LLM-ENHANCED INTRODUCTION")
        print("=" * 80)
        
        for i, step in enumerate(introduction, 1):
            print(f"\nSTEP {i}: {step['title']}")
            print("-" * 50)
            print(step['content'])
        
        print("\n" + "=" * 80)
        print("END OF LLM-ENHANCED INTRODUCTION")
        print("=" * 80)
        
        # Example of how this would be used in a frontend
        print("\nExample of JSON output for frontend:")
        print(json.dumps(introduction, indent=2))
    
    except Exception as e:
        print(f"Error during LLM-enhanced introduction generation: {str(e)}")
        print("This could be due to API limits, authentication issues, or other errors.")

if __name__ == "__main__":
    asyncio.run(main()) 