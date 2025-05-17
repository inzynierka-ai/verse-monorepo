# services/embedding.py
import openai
import logging
import os
from app.services.llm import LLMService
from app.services.llm import ModelName
from typing import Optional

# Set your API key (or load from environment)
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    # Remove newlines, as recommended by OpenAI for consistency
    text = text.replace("\n", " ")

    response = openai.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding


async def simplify_text_for_embedding(text: str, llm_service: Optional[LLMService] = None) -> str:
    """
    Use LLM to extract key words/phrases that best represent the core meaning of text.
    This optimizes text for embedding by focusing on the most semantically relevant content.
    
    Args:
        text: The original text to simplify
        llm_service: LLMService instance (if None, a new one will be created)
        
    Returns:
        A simplified version of the text containing just the key terms and concepts
    """
    # If text is too short, return as is
    if len(text) < 100:
        return text
        
    # Create LLM service if not provided
    if llm_service is None:
        from app.services.llm import LLMService
        llm_service = LLMService()
    
    # Create the system prompt
    system_prompt = """
    Extract the key terms, entities, and concepts from the provided text.
    Focus on nouns, proper names, uncommon adjectives, and domain-specific terminology.
    Format your response as a comma-separated list of terms.
    Do NOT include explanations or descriptions - only output the key terms themselves.
    Aim to preserve the core semantic meaning that would be most relevant for vector search.
    """
    
    # Create the user prompt with the text
    user_prompt = f"Extract key terms from the following text:\n\n{text}"
    
    # Generate the simplified text
    messages = [
        llm_service.create_message("system", system_prompt),
        llm_service.create_message("user", user_prompt)
    ]
    
    response = await llm_service.generate_completion(
        messages=messages,
        model=ModelName.GEMINI_2_FLASH_LITE,  # Using a fast, efficient model
        temperature=0.1,  # Low temperature for more deterministic output
        stream=False
    )
    
    simplified_text = await llm_service.extract_content(response)
    
    # Log the simplification for debugging
    logging.debug(f"Original text ({len(text)} chars) simplified to ({len(simplified_text)} chars)")
    
    return simplified_text.strip()