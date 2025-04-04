from typing import Optional, AsyncGenerator, List, Union
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_system_message_param import ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from openai.types.chat.chat_completion_assistant_message_param import ChatCompletionAssistantMessageParam


import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from enum import Enum
from langfuse.decorators import observe, langfuse_context  # type: ignore

load_dotenv()


class ModelName(str, Enum):
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"
    DEEPSEEK_V3 = 'deepseek/deepseek-chat'
    GEMINI_2_PRO = 'google/gemini-2.0-pro-exp-02-05:free'
    GEMINI_25_PRO = 'google/gemini-2.5-pro-exp-03-25:free'
    GEMINI_2_FLASH_LITE = 'google/gemini-2.0-flash-lite-001'


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
        messages: List[ChatCompletionMessageParam],
        model: ModelName = ModelName.GEMINI_2_PRO,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> AsyncGenerator[str, None] | str:
        """
        Generate a completion for the given messages.
        """
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

        try:
            response = await self.client.chat.completions.create(
                model=model.value,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            # Handle possible error response
            if not response.choices:
                # Pass the entire response object to the exception
                raise ValueError(f"Error response received: {response}")

            # Log the successful completion
            
            langfuse_context.update_current_observation(
                output=response.choices[0].message.content,
                usage=response.usage
            )
            

            return response.choices[0].message.content or ""

        except Exception as api_error:
            error_str = str(api_error)

            # Check for error response with code
            if "error" in error_str:
                self.logger.error("API error: %s", error_str)
                raise ValueError(f"API error: {error_str}") from api_error

            # Re-raise all other errors
            raise

    @observe(name="stream_completion", as_type="generation")
    async def _stream_completion(
        self,
        messages: List[ChatCompletionMessageParam],
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

            stream = await self.client.chat.completions.create(
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
            self.logger.error("Error in _stream_completion: %s", str(e))
            # Log the error to Langfuse
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=str(e)
            )
            raise

    @staticmethod
    def create_message(role: str, content: str) -> ChatCompletionMessageParam:
        """Helper method to create properly formatted messages"""
        if role == "system":
            return ChatCompletionSystemMessageParam(role=role, content=content)
        if role == "user":
            return ChatCompletionUserMessageParam(role=role, content=content)
        if role == "assistant":
            return ChatCompletionAssistantMessageParam(role=role, content=content)
        raise ValueError(f"Unsupported role: {role}")
        
    @staticmethod
    async def extract_content(response: Union[str, AsyncGenerator[str, None]]) -> str:
        """Extract string content from either str or AsyncGenerator response."""
        if isinstance(response, str):
            return response
            
        # Handle AsyncGenerator case
        result = ""
        async for chunk in response:
            result += chunk
        return result
