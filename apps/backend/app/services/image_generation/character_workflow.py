import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

import requests
from app.core.config import  settings
from .workflow_loader import WorkflowLoader


class CharacterWorkflowLoader(WorkflowLoader):
    """Loader for character generation workflows"""
    
    def __init__(self):
        super().__init__()
        self.workflow_file = "characters_api.json"
    
    def load_workflow(self, prompt: str, generation_id: str) -> Dict[str, Any]:
        """Load a character workflow and customize it with the given prompt"""
        workflow = self._load_workflow_file(self.workflow_file)
        
        if not workflow:
            logging.warning(f"Character workflow not found, using fallback")
            return {}
        
        # Customize the workflow with the prompt and random parameters
        random_seed = self._generate_random_seed()
        
        # Find the text encode node (typically contains the prompt)
        for _, node in workflow.items():
            if node.get("class_type") == "CLIPTextEncode" and "text" in node.get("inputs", {}):
                # Don't override an empty negative prompt
                if node["inputs"]["text"] != "":
                    node["inputs"]["text"] = prompt
        
        # Find the KSampler node to update random parameters
        for _, node in workflow.items():
            if node.get("class_type") == "KSampler":
                node["inputs"]["seed"] = random_seed
                node["inputs"]["steps"] = 10
                node["inputs"]["cfg"] = self._get_random_cfg()
                node["inputs"]["sampler_name"] = self._get_random_sampler()
        
        # Find the SaveImage node (if any) to add our generation ID
        for _, node in workflow.items():
            if node.get("class_type") == "SaveImage":
                node["inputs"]["filename_prefix"] = f"character_{generation_id}_{random_seed}"
                break
        else:
            # If no SaveImage node, add one connecting to the output node
            output_node_id = self._find_output_node_id(workflow)
            if output_node_id:
                new_node_id = str(max(int(k) for k in workflow.keys()) + 1)
                workflow[new_node_id] = {
                    "class_type": "SaveImage",
                    "inputs": {
                        "filename_prefix": f"character_{generation_id}_{random_seed}",
                        "images": [output_node_id, 0]
                    }
                }
        
        # Add reference image for character generation
        self._add_reference_image(workflow)
        
        return workflow
    
    def _add_reference_image(self, workflow: Dict[str, Any]) -> None:
        """Add reference image to character workflow"""
        # Find reference image path
        reference_image_path = Path(settings.MEDIA_ROOT) / "comfyui" / "reference_images" / "model_reference.jpg"
        if reference_image_path.exists():
            uploaded_image = self._upload_image(str(reference_image_path))
            if uploaded_image:
                # Find LoadImage nodes and update them with reference image
                for _node_id, node_data in workflow.get("nodes", {}).items():
                    if node_data.get("class_type") == "LoadImage":
                        # Add reference to our uploaded image
                        node_data["inputs"]["image"] = uploaded_image
                        logging.info(f"Added reference image to workflow node {_node_id}")
            else:
                logging.error("Failed to upload reference image for character generation")
        else:
            logging.error(f"Reference image not found at {reference_image_path}")

    def _upload_image(self, image_path: str) -> Optional[str]:
        """
        Method for uploading reference image to ComfyUI
        
        Args:
            image_path (str): Path to the image file
        
        Returns:
            str: Image name on the ComfyUI server or None in case of error
        """
        # Check if file exists
        if not os.path.exists(image_path):
            logging.error(f"File {image_path} does not exist")
            return None

        try:
            # Read the image file
            with open(image_path, 'rb') as file:
                image_data = file.read()

            # Create filename (using only the name without path)
            filename = os.path.basename(image_path)

            # Prepare data to send
            files = {
                'image': (filename, image_data)
            }

            # Endpoint for uploading images in ComfyUI API - using self.comfy_url
            upload_url = f"{settings.COMFYUI_API_URL}/upload/image"

            # Send POST request
            response = requests.post(upload_url, files=files)

            # Check response
            if response.status_code == 200:
                print(f"Image '{filename}' was successfully uploaded to ComfyUI")
                return filename
            else:
                print(f"Error uploading image: {response.text}")
                return None

        except Exception as e:
            logging.error(f"An error occurred while uploading the image: {str(e)}")
            return None
