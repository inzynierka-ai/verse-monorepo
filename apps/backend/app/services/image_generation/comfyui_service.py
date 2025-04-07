import os
import json
import requests
import uuid
import random
import time
import websocket
import threading
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from app.core.config import settings
import logging
from app.services.image_generation import WorkflowLoaderFactory


class ComfyUIService:
    def __init__(self):
        self.output_dir = Path(settings.MEDIA_ROOT) / "comfyui"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client_id = str(uuid.uuid4())
        # Define ComfyUI connection once
        self.hostname = "host.docker.internal"
        self.port = 8188
        self.comfy_url = f"http://{self.hostname}:{self.port}"
        self.ws_url = f"ws://{self.hostname}:{self.port}/ws?clientId={self.client_id}"

    def _queue_prompt(self, prompt, client_id=None, timeout=30):
        """Send a workflow prompt to ComfyUI's queue"""
        if client_id is None:
            client_id = self.client_id

        try:
            p = {"prompt": prompt, "client_id": client_id}
            headers = {'Content-Type': 'application/json'}
            print("Queuing the prompt")
            response = requests.post(
                f"{self.comfy_url}/prompt",
                json=p,
                headers=headers,
                timeout=timeout
            )

            if response.status_code == 400:
                logging.error(f"Error details from requests: {response.text}")
                raise ValueError(f"Bad request to ComfyUI: {response.text}")

            if response.status_code != 200:
                raise ConnectionError(
                    f"Failed to connect to ComfyUI: HTTP {response.status_code}")

            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to queue prompt: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to queue prompt: {str(e)}")

    def _track_progress(self, prompt_id: str, on_progress: Optional[Callable[[int, int], None]] = None):
        """
        Track generation progress via WebSocket
        
        Args:
            prompt_id: The ID of the prompt to track
            on_progress: Optional callback function that receives (current_step, total_steps)
        
        Returns:
            True when generation is complete
        """
        def on_message(ws, message):
            data = json.loads(message)
            if data["type"] == "progress":
                if on_progress:
                    value = data["data"]["value"]
                    max_value = data["data"]["max"]
                    on_progress(value, max_value)

            elif data["type"] == "executed" and data["data"]["prompt_id"] == prompt_id:
                ws.close()

        def on_error(ws, error):
            logging.error(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            logging.info(
                f"WebSocket connection closed: {close_status_code}, {close_msg}")

        def on_open(ws):
            logging.info("WebSocket connection established")

        ws = websocket.WebSocketApp(self.ws_url,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close,
                                    on_open=on_open)

        # Start WebSocket connection in a separate thread
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        # Wait for the thread to complete (when ws.close() is called in on_message)
        max_wait_time = 300  # 5 minutes timeout
        start_time = time.time()
        while wst.is_alive():
            if time.time() - start_time > max_wait_time:
                ws.close()
                raise TimeoutError(
                    f"Timeout waiting for generation after {max_wait_time} seconds")
            time.sleep(1)

        return True

    def _create_workflow(self, prompt: str, generation_id: str, context_type: str = "character") -> Dict[str, Any]:
        """
        Create ComfyUI workflow JSON with the given prompt and context
        
        Args:
            prompt: Text prompt for image generation
            generation_id: Unique ID for the generation
            context_type: Type of context ('character' or 'location')
            
        Returns:
            Workflow dictionary ready to be sent to ComfyUI
        """
        # Use the factory to create the appropriate loader
        loader = WorkflowLoaderFactory.create_loader(context_type)
        return loader.load_workflow(prompt, generation_id)

    def _get_history(self, prompt_id: str) -> Dict[str, Any]:
        """Get generation history from ComfyUI"""
        try:
            response = requests.get(
                f"{self.comfy_url}/history/{prompt_id}", timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logging.error(
                    f"Failed to get history, status code: {response.status_code}")
                return {}

        except Exception as e:
            logging.error(f"Error getting history: {str(e)}")
            return {}

    def _get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """Get raw image data from ComfyUI"""
        try:
            params = {
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type
            }

            logging.info(f"Fetching image from ComfyUI: {self.comfy_url}/view with params {params}")
            response = requests.get(
                f"{self.comfy_url}/view", params=params, timeout=10)

            if response.status_code == 200:
                logging.info(f"Image downloaded successfully: {len(response.content)} bytes")
                return response.content
            else:
                logging.error(
                    f"Failed to get image, status code: {response.status_code}, response: {response.text}")
                return b""

        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error getting image: {str(e)}. Check if ComfyUI is running at {self.comfy_url}")
            return b""
        except Exception as e:
            logging.error(f"Error getting image: {str(e)}")
            return b""

    def save_image_bytes(self, image_bytes: bytes, filename: str) -> str:
        """
        Save image bytes to a file in the output directory
        
        Args:
            image_bytes: The raw image data
            filename: Name for the saved file
            
        Returns:
            Path to the saved file or empty string on failure
        """
        try:
            if not image_bytes:
                logging.error("Cannot save empty image data")
                return ""
                
            # Create full path within output directory
            file_path = self.output_dir / filename
            
            # Write bytes to file
            with open(file_path, "wb") as f:
                f.write(image_bytes)
                
            logging.info(f"Image saved to {file_path}")
            return str(file_path)
            
        except Exception as e:
            logging.error(f"Error saving image: {str(e)}")
            return ""

    def generate_image(self, prompt: str, context_type: str = "character") -> Dict[str, Any]:
        """
        Generate an image from a text prompt and save it to disk
        
        Args:
            prompt: Text description for image generation
            context_type: Type of context ('character' or 'location')
            
        Returns:
            Dictionary with image information
        """
        try:
            logging.info(f"Starting image generation for prompt: '{prompt}' (context: {context_type})")
            
            
            # Create a unique ID for this generation
            generation_id = str(uuid.uuid4())[:8]
            logging.debug(f"Generation ID: {generation_id}")
            
            # Create workflow with the prompt and context
            logging.debug(f"Creating workflow with prompt: '{prompt}'")
            workflow = self._create_workflow(prompt, generation_id, context_type)
            logging.debug(f"Workflow created successfully")
            
            # Queue the prompt and get prompt ID
            logging.info(f"Queuing workflow to ComfyUI")
            queue_response = self._queue_prompt(workflow)
            if not queue_response or "prompt_id" not in queue_response:
                logging.error(f"Failed to queue prompt. Response: {queue_response}")
                return {"success": False, "error": "Failed to queue prompt", "imagePath": ""}
                
            prompt_id = queue_response["prompt_id"]
            logging.info(f"Prompt queued with ID: {prompt_id}")
            
            # Track progress until completion
            logging.info(f"Tracking generation progress...")
            self._track_progress(prompt_id, 
                               on_progress=lambda value, max_value: 
                                   logging.info(f"Generation progress: {value}/{max_value}"))
            
            logging.info(f"Generation complete, retrieving history")
            
            # Get history to find output image
            history = self._get_history(prompt_id)
            if not history:
                logging.error("Failed to get generation history - empty response")
                return {"success": False, "error": "Failed to get generation history", "imagePath": ""}
                
            logging.debug(f"History data: {json.dumps(history, indent=2)}")
            
            # Extract image filename from history
            try:
                logging.debug("Parsing history to find output image")
                
                # Get outputs from the prompt history
                prompt_outputs = history.get(prompt_id, {}).get("outputs", {})
                if not prompt_outputs:
                    logging.error(f"No outputs found in history for prompt ID: {prompt_id}")
                    return {"success": False, "error": "No outputs in history", "imagePath": ""}
                
                # Find the first node with images
                image_data = None
                for _, node_output in prompt_outputs.items():
                    if "images" in node_output and node_output["images"]:
                        image_data = node_output["images"][0]
                        break
                
                if not image_data:
                    logging.error("No images found in history")
                    return {"success": False, "error": "No images found in history", "imagePath": ""}
                    
                filename = image_data.get("filename")
                subfolder = image_data.get("subfolder", "")
                type = image_data.get("type", "")
                
                if not filename:
                    logging.error("Image filename not found in history")
                    return {"success": False, "error": "Image filename not found", "imagePath": ""}
                
                logging.info(f"Found image: {filename} in folder: {subfolder}")
                    
                # Get the image data
                logging.info(f"Downloading image from ComfyUI")
                image_bytes = self._get_image(filename, subfolder, type)
                if not image_bytes:
                    logging.error("Failed to download image - empty response")
                    return {"success": False, "error": "Failed to download image", "imagePath": ""}
                
                logging.debug(f"Downloaded image size: {len(image_bytes)} bytes")
                    
                # Save the image locally
                local_filename = f"{generation_id}_{filename}"
                logging.info(f"Saving image as: {local_filename}")
                file_path = self.save_image_bytes(image_bytes, local_filename)
                
                if not file_path:
                    logging.error("Failed to save image locally")
                    return {"success": False, "error": "Failed to save image locally", "imagePath": ""}
                
                # Create relative path for frontend
                relative_path = f"/media/comfyui/{os.path.basename(file_path)}"
                
                logging.info(f"Image generation complete. Saved to: {file_path}")
                return {
                    "success": True,
                    "imagePath": relative_path,
                    "promptId": prompt_id,
                    "imagePaths": {
                        "base": f"/media/comfyui",
                        "images": [os.path.basename(file_path)]
                    }
                }
                
            except (KeyError, IndexError) as e:
                logging.error(f"Error parsing history: {str(e)}")
                logging.debug(f"History structure: {history}")
                return {"success": False, "error": f"Error parsing history: {str(e)}", "imagePath": ""}
                
        except Exception as e:
            logging.error(f"Error generating image: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return {"success": False, "error": f"Error generating image: {str(e)}", "imagePath": ""}
