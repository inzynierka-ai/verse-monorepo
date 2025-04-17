from typing import Optional, AsyncGenerator, List, Union, Dict, Any
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_system_message_param import ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from openai.types.chat.chat_completion_assistant_message_param import ChatCompletionAssistantMessageParam
import json


from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from enum import Enum
from langfuse.decorators import observe, langfuse_context  # type: ignore

from app.core.config import settings

load_dotenv()


class ModelProvider(str, Enum):
    OPENAI = "openai"
    OPENROUTER = "openrouter"


class ModelName(Enum):
    GPT4O = ("gpt-4o", ModelProvider.OPENAI)
    GPT4O_MINI = ("gpt-4o-mini", ModelProvider.OPENAI)
    GPT41 = ('gpt-4.1-2025-04-14', ModelProvider.OPENAI)
    GPT41_MINI = ("gpt-4.1-mini-2025-04-14", ModelProvider.OPENAI)
    DEEPSEEK_V3 = ('deepseek/deepseek-chat', ModelProvider.OPENROUTER)
    GEMINI_2_PRO = ('google/gemini-2.0-pro-exp-02-05:free', ModelProvider.OPENROUTER)
    GEMINI_25_PRO = ('google/gemini-2.5-pro-exp-03-25:free', ModelProvider.OPENROUTER)
    GEMINI_2_FLASH_LITE = ('google/gemini-2.0-flash-lite-001', ModelProvider.OPENROUTER)
    
    def __init__(self, model_id: str, provider: ModelProvider):
        self.model_id = model_id
        self.provider = provider
        
    @property
    def value(self) -> str:
        """For backwards compatibility with code expecting value to be the model ID"""
        return self.model_id


class LLMService:
    def __init__(self, openai_api_key: Optional[str] = None, openrouter_api_key: Optional[str] = None):
        # Initialize OpenAI client
        self.openai_client = AsyncOpenAI(
            api_key=openai_api_key or settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
        )
        
        # Initialize OpenRouter client
        self.openrouter_client = AsyncOpenAI(
            api_key=openrouter_api_key or settings.OPEN_ROUTER_API_KEY,
            base_url=settings.OPEN_ROUTER_API_BASE,
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _get_client_for_model(self, model: ModelName):
        """Get the appropriate client based on the model provider"""
        if model.provider == ModelProvider.OPENAI:
            return self.openai_client
        elif model.provider == ModelProvider.OPENROUTER:
            return self.openrouter_client
        else:
            raise ValueError(f"Unsupported model provider: {model.provider}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    @observe(name="generate_completion", as_type="generation")
    async def generate_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: ModelName = ModelName.GPT41_MINI,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        metadata: Optional[Dict[str, str]] = None,
    ) -> AsyncGenerator[str, None] | str:
        """
        Generate a completion for the given messages.
        """
        # Add metadata to the current span
        langfuse_context.update_current_observation(
            metadata={
                "model": model.model_id,
                "provider": model.provider.value,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
                "messages_count": len(messages),
                "metadata": metadata
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
            # Get the appropriate client for this model
            client = self._get_client_for_model(model)
            
            response = await client.chat.completions.create(
                model=model.model_id,
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
            
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    @observe(name="generate_response", as_type="generation")
    async def generate_response(
        self,
        input_text: str,
        model: ModelName = ModelName.GPT41,
        temperature: float = 0.7,
        instructions: Optional[str] = None,
        max_output_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        previous_response_id: Optional[str] = None,
        stream: bool = False,
        text_format: Dict[str, str] = {"type": "text"},
        metadata: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Generate a response using OpenAI's Responses API with function calling support.
        
        Args:
            input_text: Text input to the model
            model: Model to use
            temperature: Sampling temperature
            instructions: System instructions (like system message)
            max_output_tokens: Maximum tokens to generate
            tools: List of tool definitions for function calling
            tool_choice: How the model should select tools
            previous_response_id: ID of previous response for conversation continuity
            stream: Whether to stream the response
            text_format: Format of the text response
            metadata: Additional metadata for the request
            
        Returns:
            The complete response object from the Responses API
        """
        # Add metadata to the current span
        langfuse_metadata: Dict[str, Any] = {
            "model": model.model_id,
            "provider": model.provider.value,
            "temperature": temperature,
            "stream": stream,
            "has_previous_response": previous_response_id is not None
        }
        
        if max_output_tokens:
            langfuse_metadata["max_output_tokens"] = max_output_tokens
        
        if tools:
            langfuse_metadata["tools_count"] = len(tools)
            
        langfuse_context.update_current_observation(metadata=langfuse_metadata)
        
        try:
            # Get the appropriate client for this model
            client = self._get_client_for_model(model)
            
            # Build request parameters
            request_params: Dict[str, Any] = {
                "model": model.model_id,
                "input": input_text,
                "temperature": temperature,
                "stream": stream
            }
            
            # Add optional parameters
            if instructions:
                request_params["instructions"] = instructions
            if max_output_tokens:
                request_params["max_output_tokens"] = max_output_tokens
            if tools:
                request_params["tools"] = tools
            if tool_choice:
                request_params["tool_choice"] = tool_choice
            if previous_response_id:
                request_params["previous_response_id"] = previous_response_id
            if text_format:
                request_params["text"] = {"format": text_format}
            if metadata:
                request_params["metadata"] = metadata
                
            # Call the Responses API
            response: Any = await client.responses.create(**request_params)
            
            # Log the completion outcomes
            extracted_data = self._extract_response_data(response)
            
            # Log to langfuse
            usage_data = response.usage if hasattr(response, "usage") else None
            langfuse_context.update_current_observation(
                output=response.to_dict()["output"],
                metadata={
                    "function_calls": extracted_data.get("function_calls", []),
                    "has_function_calls": bool(extracted_data.get("function_calls"))
                },
                usage=usage_data
            )
            
            return response
            
        except Exception as api_error:
            error_str = str(api_error)
            self.logger.error("API error in generate_response: %s", error_str)
            
            # Log the error to Langfuse
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=error_str
            )
            
            raise ValueError(f"API error in generate_response: {error_str}") from api_error
            
    def _extract_response_data(self, response: Any) -> Dict[str, Any]:
        """
        Extract text and function calls from the response.
        
        Args:
            response: The response from the OpenAI Responses API
            
        Returns:
            A dictionary with "text" and "function_calls" keys
        """
        result: Dict[str, Any] = {
            "text": "",
            "function_calls": []
        }
        
        try:
            if not hasattr(response, "output") or not response.output:
                return result
                
            for item in response.output:
                # Handle text output
                if hasattr(item, "type") and item.type == "message" and hasattr(item, "content"):
                    for content in item.content:
                        if (hasattr(content, "type") and 
                            content.type == "output_text" and 
                            hasattr(content, "text")):
                            result["text"] += content.text
                
                # Handle function calls
                elif hasattr(item, "type") and item.type == "function_call":
                    function_call: Dict[str, Any] = {
                        "name": item.name if hasattr(item, "name") else None,
                        "arguments": json.loads(item.arguments) if hasattr(item, "arguments") else {},
                        "id": item.id if hasattr(item, "id") else None,
                        "call_id": item.call_id if hasattr(item, "call_id") else None,
                        "status": item.status if hasattr(item, "status") else None
                    }
                    result["function_calls"].append(function_call)
                    
        except (AttributeError, TypeError, IndexError, json.JSONDecodeError) as e:
            self.logger.warning(f"Error extracting data from response: {e}")
            
        return result
    
    @staticmethod
    async def extract_function_calls(response: Any) -> List[Dict[str, Any]]:
        """
        Extract function calls from a response.
        
        Args:
            response: The response from the OpenAI Responses API
            
        Returns:
            A list of function call objects with name, arguments, and other metadata
        """
        function_calls: List[Dict[str, Any]] = []
        
        try:
            if hasattr(response, "output") and response.output:
                for item in response.output:
                    if hasattr(item, "type") and item.type == "function_call":
                        function_call: Dict[str, Any] = {
                            "name": item.name if hasattr(item, "name") else None,
                            "arguments": json.loads(item.arguments) if hasattr(item, "arguments") else {},
                            "id": item.id if hasattr(item, "id") else None,
                            "call_id": item.call_id if hasattr(item, "call_id") else None,
                            "status": item.status if hasattr(item, "status") else None
                        }
                        function_calls.append(function_call)
        except (AttributeError, TypeError, json.JSONDecodeError):
            # Return empty list in case of errors
            pass
            
        return function_calls

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
                    "model": model.model_id,
                    "provider": model.provider.value,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                    "messages_count": len(messages)
                }
            )

            # Get the appropriate client for this model
            client = self._get_client_for_model(model)
            
            stream = await client.chat.completions.create(
                model=model.model_id,
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
        
    @staticmethod
    def create_tool(function_def: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to create a properly formatted tool for function calling"""
        return {
            "type": "function",
            **function_def
        }
