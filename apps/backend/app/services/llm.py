from typing import Optional, AsyncGenerator, List, Dict, Any
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion import Choice
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from enum import Enum
from langfuse.decorators import observe, langfuse_context

load_dotenv()

class ModelName(str, Enum):
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"
    DEEPSEEK_V3='deepseek/deepseek-chat'
    GEMINI_2_PRO='google/gemini-2.0-pro-exp-02-05:free'
    GEMINI_2_FLASH_LITE='google/gemini-2.0-flash-lite-preview-02-05:free'

class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"), 
        )
        self.logger = logging.getLogger(__name__)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    @observe(name="generate_completion", as_type="generation")
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: ModelName = ModelName.GEMINI_2_PRO,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> AsyncGenerator[str, None] | str:
        try:
            # Add metadata to the current span
            langfuse_context.update_current_observation(
                metadata={
                    "model": model.value,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": stream,
                    "messages_count": len(messages)
                }
            )
            
            if stream:
                return self._stream_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            
            response: ChatCompletion = await self.client.chat.completions.create(
                model=model.value,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            # Debug information
            if response is None:
                self.logger.error("API response is None")
                raise ValueError("API response is None")
                
            if not hasattr(response, 'choices') or response.choices is None:
                self.logger.error("Response has no 'choices' attribute or it's None", response)
                raise ValueError("Response has no choices")
                
            if len(response.choices) == 0:
                self.logger.error("Response choices list is empty", response)
                raise ValueError("Response choices list is empty")  
                
            if not hasattr(response.choices[0], 'message'):
                self.logger.error("First choice has no 'message' attribute", response)
                raise ValueError("First choice has no message")
                
            # Log the successful completion
            try:
                langfuse_context.update_current_observation(
                    output=response.choices[0].message.content,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                )
            except Exception as log_error:
                self.logger.error(f"Error during logging to Langfuse: {str(log_error)}")
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            self.logger.error(f"Error in generate_completion: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Log the error to Langfuse
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=str(e)
            )
            raise

    @observe(name="stream_completion", as_type="span")
    async def _stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: ModelName,
        temperature: float,
        max_tokens: Optional[int]
    ) -> AsyncGenerator[str, None]:
        try:
            # Add metadata to the current span
            langfuse_context.update_current_observation(
                metadata={
                    "model": model.value,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                    "messages_count": len(messages)
                }
            )
            
            stream: AsyncGenerator[ChatCompletionChunk, None] = await self.client.chat.completions.create(
                model=model.value,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # Log the complete streamed response when done
            langfuse_context.update_current_observation(
                output=full_response
            )
                    
        except Exception as e:
            self.logger.error(f"Error in _stream_completion: {str(e)}")
            # Log the error to Langfuse
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=str(e)
            )
            raise

    @staticmethod
    def create_message(role: str, content: str) -> Dict[str, str]:
        """Helper method to create properly formatted messages"""
        return {"role": role, "content": content} 