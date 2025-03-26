from typing import Optional, AsyncGenerator, List
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
    GEMINI_2_FLASH_LITE = 'google/gemini-2.0-flash-lite-preview-02-05:free'


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

            response = await self.client.chat.completions.create(
                model=model.value,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            if len(response.choices) == 0:
                self.logger.error("Response choices list is empty: %s", response)
                raise ValueError("Response choices list is empty")

            if not hasattr(response.choices[0], 'message'):
                self.logger.error("First choice has no 'message' attribute: %s", response)
                raise ValueError("First choice has no message")

            # Log the successful completion
            try:
                langfuse_context.update_current_observation(
                    output=response.choices[0].message.content,
                    usage=response.usage
                )
            except Exception as log_error:
                self.logger.error("Error during logging to Langfuse: %s", str(log_error))

            return response.choices[0].message.content or ""

        except Exception as e:
            self.logger.error("Error in generate_completion: %s", str(e))
            import traceback
            self.logger.error("Traceback: %s", traceback.format_exc())

            # Log the error to Langfuse
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=str(e)
            )
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
