import json
import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from app.core.config import settings


class WorkflowLoader(ABC):
    """Abstract base class for loading ComfyUI workflows from JSON files"""

    def __init__(self):
        """Initialize the workflow loader"""
        self.workflow_dir = Path(settings.COMFYUI_WORKFLOWS_DIR)

    @abstractmethod
    def load_workflow(self, prompt: str, generation_id: str) -> Dict[str, Any]:
        """
        Load a workflow from a JSON file and customize it with the given prompt

        Args:
            prompt: Text prompt for image generation
            generation_id: Unique ID for the generation

        Returns:
            Workflow dictionary ready to be sent to ComfyUI
        """

    def _load_workflow_file(self, filename: str) -> Dict[str, Any]:
        """
        Load a workflow from a JSON file

        Args:
            filename: Name of the JSON file to load

        Returns:
            Loaded workflow as a dictionary
        """
        filepath = self.workflow_dir / filename
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Workflow file not found: {filepath}")
            # Return an empty workflow as fallback
            return {}
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in workflow file: {filepath}")
            return {}

    def _generate_random_seed(self) -> int:
        """Generate a random seed for the workflow"""
        return random.randint(1, 2147483647)

    def _find_output_node_id(self, workflow: Dict[str, Any]) -> Optional[str]:
        """Find the ID of the output node in the workflow"""
        for node_id, node in workflow.items():
            if node.get("class_type") in ["VAEDecode", "PreviewImage"]:
                return node_id
        return None
