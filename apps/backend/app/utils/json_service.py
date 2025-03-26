from typing import Dict, Any, List, Type, TypeVar
import json
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)

class JSONService:
    @staticmethod
    def extract_json_from_response(response: str) -> str:
        """
        Extract JSON content from a response that might contain markdown.
        
        Args:
            response: The response text
            
        Returns:
            Extracted JSON content as string
        """
        if "```json" in response:
            return response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            return response.split("```")[1].split("```")[0].strip()
        else:
            return response.strip()
    
    @staticmethod
    def parse_json_response(response: str) -> Dict[str, Any]:
        """
        Parse a JSON response into a dictionary.
        
        Args:
            response: The LLM response text
            
        Returns:
            Dictionary containing parsed JSON data
        """
        if not response:
            raise ValueError("Empty response received from LLM")
            
        # Try to extract JSON from markdown code blocks if present
        json_content = JSONService.extract_json_from_response(response)
        print(f"JSON content: {json_content}")
        
        try:
            data = json.loads(json_content)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}") from e
    
    @staticmethod
    def parse_and_validate_json_response(response: str, model_class: Type[T]) -> T:
        """
        Parse a JSON response and validate it against a Pydantic model.
        
        Args:
            response: The LLM response text
            model_class: Pydantic model class to validate against
            
        Returns:
            Validated model instance
        """
        data = JSONService.parse_json_response(response)
        
        try:
            return model_class.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"JSON validation failed: {str(e)}") from e
    
    @staticmethod
    def parse_and_validate_json_list(response: str, model_class: Type[T]) -> List[T]:
        """
        Parse a JSON list response and validate each item against a Pydantic model.
        
        Args:
            response: The LLM response text
            model_class: Pydantic model class to validate each item against
            
        Returns:
            List of validated model instances
        """
        data = JSONService.parse_json_response(response)
        
        if not isinstance(data, list):
            raise ValueError(f"Expected JSON list but got {type(data).__name__}")
        
        result = []
        for i, item in enumerate(data):
            try:
                validated_item = model_class.model_validate(item)
                result.append(validated_item)
            except ValidationError as e:
                raise ValueError(f"Validation failed for item {i}: {str(e)}") from e
        
        return result 