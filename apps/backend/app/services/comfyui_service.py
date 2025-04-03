import os
import json
import requests
import uuid
from typing import Dict, Any, List
from pathlib import Path
from app.core.config import settings

class ComfyUIService:
    def __init__(self):
        import logging
        self.comfyui_api_url = settings.COMFYUI_API_URL
        self.output_dir = Path(settings.MEDIA_ROOT) / "comfyui"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.workflow_path = Path(settings.COMFYUI_WORKFLOWS_DIR) / "characters_api.json"
        self.client_id = str(uuid.uuid4())
        logging.info(f"Initializing ComfyUIService with API URL: {self.comfyui_api_url}")

    def _queue_prompt(self, prompt, client_id=None, timeout=30):
        """Send a workflow prompt to ComfyUI's queue"""
        import logging
        if client_id is None:
            client_id = self.client_id
        
        # Force the hostname to match config
        hostname = "host.docker.internal"
        port = 8188
        comfy_url = f"http://{hostname}:{port}"
        
        try:
            p = {"prompt": prompt, "client_id": client_id}
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(
                f"{comfy_url}/prompt", 
                json=p,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 400:
                logging.error(f"Error details from requests: {response.text}")
            return response.json()
        except Exception as e:
            logging.error(f"Failed to queue prompt: {str(e)}")
            raise Exception(f"Failed to queue prompt: {str(e)}")
            
    async def generate_image_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate image using ComfyUI based on text prompt"""
        import logging
        
        generation_id = str(uuid.uuid4())
        output_path = self.output_dir / generation_id
        output_path.mkdir(exist_ok=True)
        
        # Save generation ID as instance attribute to be available in _wait_for_generation
        self.current_generation_id = generation_id
        
        # Prepare workflow for ComfyUI
        workflow = self._create_workflow(prompt, str(output_path))
        
        try:
            response_data = self._queue_prompt(workflow)
            
            # Get the prompt ID from the response
            prompt_id = response_data.get("prompt_id")
            if not prompt_id:
                raise ValueError("No prompt_id in response from ComfyUI")
                
            # Wait for the image generation to complete
            image_paths = self._wait_for_generation(prompt_id)
            
            # Return the relative paths to the generated images
            return {
                "imagePaths": {
                    "base": f"/media/comfyui/{generation_id}",
                    "images": image_paths
                }
            }
        except Exception as e:
            logging.error(f"Error queuing prompt to ComfyUI: {str(e)}")
            raise
    
    def _create_workflow(self, prompt: str, output_path: str) -> Dict:
        """Create ComfyUI workflow JSON with the given prompt and output path"""
        import random
        
        # Get generation ID
        generation_id = os.path.basename(output_path)
        
        # Generate random seed for unique images
        random_seed = random.randint(1, 2147483647)
        random_steps = random.randint(20, 40)
        random_cfg = round(random.uniform(6.5, 8.5), 1)
        
        # List of samplers to randomly choose from
        samplers = ["euler", "euler_ancestral", "heun", "dpm_2", "dpm_2_ancestral", "lms", "ddim"]
        random_sampler = random.choice(samplers)
        
        # Workflow with random parameters for unique generation but same model
        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "dreamshaper_8.safetensors"
                }
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                }
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "bad quality, blurry, deformed, ugly, low resolution",
                    "clip": ["1", 1]
                }
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": 512,
                    "height": 512,
                    "batch_size": 1
                }
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": random_seed,
                    "steps": random_steps,
                    "cfg": random_cfg,
                    "sampler_name": random_sampler,
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0]
                }
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                }
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": f"generated_{generation_id}_{str(random_seed)}",
                    "images": ["6", 0]
                }
            }
        }
    
    def _wait_for_generation(self, prompt_id: str, timeout: int = 300, polling_interval: int = 5) -> List[str]:
        """Wait for ComfyUI to complete image generation and return paths"""
        import logging
        import time
        import shutil
        import os
        import requests
        from pathlib import Path
        from app.core.config import settings
        
        # Use saved generation ID
        target_dir = Path(settings.MEDIA_ROOT) / "comfyui" 
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Use path from configuration - should now point to mounted volume
        comfyui_output_dir = settings.COMFYUI_DEFAULT_OUTPUT_DIR
        
        # Force the hostname to match config
        hostname = "host.docker.internal"
        port = 8188
        comfy_url = f"http://{hostname}:{port}"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{comfy_url}/history/{prompt_id}")
                
                if response.status_code == 200:
                    history = response.json()
                    
                    # Check if the task is completed
                    if prompt_id in history and "outputs" in history[prompt_id]:
                        outputs = history[prompt_id]["outputs"]
                        image_paths = []
                        
                        # Search outputs for all nodes generating images
                        for node_id, node_output in outputs.items():
                            if "images" in node_output:
                                for img in node_output["images"]:
                                    filename = img.get("filename")
                                    if filename:
                                        # Full path to file in ComfyUI output folder
                                        source_path = os.path.join(comfyui_output_dir, filename)
                                        
                                        # Full target path in our project
                                        target_path = os.path.join(str(target_dir), os.path.basename(filename))
                                        
                                        # Copy file to our directory
                                        if os.path.exists(source_path):
                                            shutil.copy2(source_path, target_path)
                                            image_paths.append(os.path.basename(filename))
                        
                        if image_paths:
                            return image_paths
                
                # If no results found, wait and try again
                time.sleep(polling_interval)
                
            except Exception as e:
                logging.error(f"Error while checking ComfyUI status: {str(e)}")
                time.sleep(polling_interval)
        
        # After timeout, raise error
        raise TimeoutError(f"Timeout waiting for image generation after {timeout} seconds")