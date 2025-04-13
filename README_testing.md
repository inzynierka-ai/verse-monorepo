# Character Generator Testing

This directory contains tests for the `character_generator.py` module to validate the character generation workflow.

## Available Tests

1. **Basic Test (`test_character_generator.py`)**:
   - Tests the `create_character_json` function
   - Validates that the output is valid JSON
   - Checks for required fields
   - Saves the result to a file

2. **Comprehensive Test (`test_character_generator_full.py`)**:
   - Tests all main functions: `create_character_prompt`, `describe_character`, `create_character_json`, and `generate_image_prompt`
   - Validates each step of the workflow
   - Performs assertions on the outputs
   - Saves the final character to a JSON file

## Running the Tests

Make sure you're in the correct directory and have the backend environment activated:

```bash
# Activate the virtual environment if you haven't already
source .venv/bin/activate

# Run the basic test
python test_character_generator.py

# Run the comprehensive test
python test_character_generator_full.py
```

## Test Output

Both tests will:
1. Print progress and validation results to the console
2. Save the generated character to a JSON file in the `test_output` directory
3. Generate a unique filename with a timestamp

## Extending the Tests

To create additional tests:

1. **Test with different inputs**: Modify the `story` and `character_draft` objects in either test file
2. **Add more assertions**: Add additional validation checks for the character fields
3. **Test specific edge cases**: Create versions that test specific scenarios or boundary conditions

## Considerations for LLM-Based Testing

Since character generation relies on LLM services:

1. **API availability**: Tests require connectivity to the LLM API service
2. **Cost awareness**: Running tests incurs API costs for each LLM call
3. **Determinism**: LLM responses vary, so some test failures may be due to LLM variability
4. **Response time**: Tests may take longer to complete due to API call latency

## Using with PromptFoo (Alternative)

If you want to isolate and test just the prompts:

1. Set up PromptFoo using the provided configuration in the `promptfoo` directory
2. Use it to test and compare individual prompts
3. Optimize prompt templates based on PromptFoo feedback
4. Incorporate improved prompts back into the character generator code 