# services/embedding.py
import openai
import os

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
