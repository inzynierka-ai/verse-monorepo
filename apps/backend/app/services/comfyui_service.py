import os
import json
import socket  # Dodaj ten import
import requests
import uuid
import urllib.request
import urllib.error
from typing import Dict, Any, List
from pathlib import Path
from app.core.config import settings

class ComfyUIService:
    def __init__(self):
        import logging
        self.comfyui_api_url = settings.COMFYUI_API_URL
        logging.info(f"COMFYUI URL FROM SETTINGS: {self.comfyui_api_url}")
        
        self.output_dir = Path(settings.MEDIA_ROOT) / "comfyui"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.workflow_path = Path(settings.COMFYUI_WORKFLOWS_DIR) / "characters_api.json"
        
        # Check if workflow file exists
        logging.info(f"Checking workflow path: {self.workflow_path}")
        if not self.workflow_path.exists():
            logging.error(f"Workflow file does not exist: {self.workflow_path}")
            # List files in the directory to help debug
            try:
                workflow_dir = Path(settings.COMFYUI_WORKFLOWS_DIR)
                if workflow_dir.exists():
                    logging.info(f"Files in {workflow_dir}:")
                    for f in workflow_dir.iterdir():
                        logging.info(f"  {f}")
                else:
                    logging.error(f"Workflow directory does not exist: {workflow_dir}")
            except Exception as e:
                logging.error(f"Error listing workflow directory: {e}")
        
        self.client_id = str(uuid.uuid4())
        
        # Test connection to ComfyUI
        logging.info(f"Initializing ComfyUIService with API URL: {self.comfyui_api_url}")
        self._test_connection()

    def _test_connection(self):
        """Test connection to ComfyUI server"""
        import logging
        
        # Extract hostname and port from URL
        from urllib.parse import urlparse
        parsed_url = urlparse(self.comfyui_api_url)
        
        # Force the hostname to match config
        hostname = "host.docker.internal"  # Wymuszamy poprawny adres
        port = 8188
        
        logging.info(f"Testing connection to FORCED {hostname}:{port}")
        
        # Try socket connection first to test basic connectivity
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((hostname, port))
            s.close()
            logging.info(f"Socket connection successful to {hostname}:{port}")
        except Exception as e:
            logging.error(f"Socket connection failed to {hostname}:{port}: {e}")
        
        # Now try HTTP request with FORCED URL
        try:
            test_url = f"http://{hostname}:{port}/system_stats"
            logging.info(f"Trying HTTP request to {test_url}")
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                logging.info(f"Successfully connected to ComfyUI at {test_url}")
            else:
                logging.warning(f"ComfyUI responded with status code {response.status_code}")
        except Exception as e:
            logging.error(f"Failed to connect to ComfyUI at {test_url}: {e}")
            logging.info("Please ensure ComfyUI is running and accessible from Docker")

    def _queue_prompt(self, prompt, client_id=None, timeout=30):
        """
        Send a workflow prompt to ComfyUI's queue
        """
        import logging
        if client_id is None:
            client_id = self.client_id
        
        # Force the hostname to match config
        hostname = "host.docker.internal"
        port = 8188
        comfy_url = f"http://{hostname}:{port}"
        
        logging.info(f"Sending prompt to FORCED URL: {comfy_url}/prompt")
        
        try:
            # Sprawdź format promptu
            logging.info(f"Prompt type: {type(prompt)}")
            
            # Zapisz pełną zawartość promptu do pliku dla debugowania
            debug_file = Path("/tmp/comfyui_prompt_debug.json")
            with open(debug_file, "w") as f:
                json.dump(prompt, f, indent=2)
            logging.info(f"Saved complete prompt to {debug_file}")
            
            p = {"prompt": prompt, "client_id": client_id}
            headers = {'Content-Type': 'application/json'}
            
            data = json.dumps(p).encode('utf-8')
            
            # Wypróbuj alternatywne podejście z requests
            try:
                logging.info("Trying with requests library...")
                response = requests.post(
                    f"{comfy_url}/prompt", 
                    json=p,
                    headers=headers,
                    timeout=timeout
                )
                logging.info(f"Requests response status: {response.status_code}")
                if response.status_code == 400:
                    logging.error(f"Error details from requests: {response.text}")
                return response.json()
            except Exception as req_e:
                logging.error(f"Requests approach failed: {req_e}, falling back to urllib")
            
            # Oryginalne podejście
            req = urllib.request.Request(
                f"{comfy_url}/prompt",
                data=data, 
                headers=headers
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_data = response.read()
                logging.info(f"Response status: {response.status}")
                return json.loads(response_data)
        except urllib.error.HTTPError as e:
            # Log detailed error for HTTP errors
            logging.error(f"HTTP Error: {e.code} - {e.reason}")
            if hasattr(e, 'read'):
                error_content = e.read().decode('utf-8')
                logging.error(f"Error content: {error_content}")
            raise Exception(f"Failed to queue prompt: {str(e)}")
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
            logging.error(f"Error details: {e}")
            raise Exception(f"Failed to queue prompt: {str(e)}")
            
    async def generate_image_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate image using ComfyUI based on text prompt"""
        # Create unique ID for this generation
        import logging
        
        generation_id = str(uuid.uuid4())
        output_path = self.output_dir / generation_id
        output_path.mkdir(exist_ok=True)
        
        # Zapisz ID generacji jako atrybut instancji, aby był dostępny w _wait_for_generation
        self.current_generation_id = generation_id
        
        # Prepare workflow for ComfyUI
        workflow = self._create_workflow(prompt, str(output_path))
        
        # Send request to ComfyUI using the queue_prompt method
        try:
            logging.info(f"Sending prompt to ComfyUI: {self.comfyui_api_url}")
            
            response_data = self._queue_prompt(workflow)
            logging.info(f"Received response: {response_data}")
            
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
            # Log the error and re-raise
            logging.error(f"Error queuing prompt to ComfyUI: {str(e)}")
            raise
    
    def _create_workflow(self, prompt: str, output_path: str) -> Dict:
        """Create ComfyUI workflow JSON with the given prompt and output path"""
        import logging
        import os
        import random
        
        # Get generation ID
        generation_id = os.path.basename(output_path)
        
        # Make sure the target directory exists
        target_dir = os.path.join(r"C:\Users\Marta\projekt\verse-monorepo\apps\backend\media\comfyui", generation_id)
        os.makedirs(target_dir, exist_ok=True)
        
        logging.info(f"Container path: {output_path}")
        logging.info(f"Generation ID: {generation_id}")
        
        # Generate random seed for unique images
        random_seed = random.randint(1, 2147483647)
        
        # Randomly vary parameters that affect generation while keeping the model
        random_steps = random.randint(20, 40)
        random_cfg = round(random.uniform(6.5, 8.5), 1)
        
        # List of samplers to randomly choose from
        samplers = ["euler", "euler_ancestral", "heun", "dpm_2", "dpm_2_ancestral", "lms", "ddim"]
        random_sampler = random.choice(samplers)
        
        logging.info(f"Creating dynamic workflow with seed={random_seed}, steps={random_steps}, cfg={random_cfg}, sampler={random_sampler}")
        
        # Workflow with random parameters for unique generation but same model
        dynamic_workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "dreamshaper_8.safetensors"  # Keeping the existing model
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
                    # Removed output_dir parameter - ComfyUI will use default folder
                }
            }
        }
        
        logging.info(f"Using dynamic workflow with dreamshaper model and randomized parameters")
        return dynamic_workflow
    
    def _wait_for_generation(self, prompt_id: str, timeout: int = 300, polling_interval: int = 5) -> List[str]:
        """Wait for ComfyUI to complete image generation and return paths"""
        import logging
        import time
        import shutil
        import os
        import requests
        from pathlib import Path
        from app.core.config import settings
        
        logging.info(f"Waiting for ComfyUI generation with prompt_id {prompt_id}")
        
        #Używamy zapisanego ID generacji
        generation_id = self.current_generation_id
        target_dir = Path(settings.MEDIA_ROOT) / "comfyui" 
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Używamy ścieżki z konfiguracji - powinna teraz wskazywać na zamontowany wolumin
        comfyui_output_dir = settings.COMFYUI_DEFAULT_OUTPUT_DIR
        
        # Force the hostname to match config
        hostname = "host.docker.internal"
        port = 8188
        comfy_url = f"http://{hostname}:{port}"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{comfy_url}/history/{prompt_id}")
                logging.info(f"Sprawdzanie statusu pod adresem: {comfy_url}/history/{prompt_id}, kod: {response.status_code}")
                
                if response.status_code == 200:
                    history = response.json()
                    
                    # Sprawdź czy zadanie zostało ukończone
                    if prompt_id in history and "outputs" in history[prompt_id]:
                        outputs = history[prompt_id]["outputs"]
                        image_paths = []
                        
                        # Przeszukaj outputy po wszystkich węzłach generujących obrazy
                        for node_id, node_output in outputs.items():
                            if "images" in node_output:
                                for img in node_output["images"]:
                                    filename = img.get("filename")
                                    if filename:
                                        logging.info(f"ComfyUI zwrócił nazwę pliku: {filename}")
                                        
                                        # Pełna ścieżka do pliku w folderze wyjściowym ComfyUI
                                        source_path = os.path.join(comfyui_output_dir, filename)
                                        
                                        # Pełna ścieżka docelowa w naszym projekcie
                                        target_path = os.path.join(str(target_dir), os.path.basename(filename))
                                        
                                        # Kopiujemy plik do naszego katalogu
                                        if os.path.exists(source_path):
                                            shutil.copy2(source_path, target_path)
                                            logging.info(f"Skopiowano obraz z {source_path} do {target_path}")
                                            image_paths.append(os.path.basename(filename))
                                        else:
                                            logging.error(f"Nie znaleziono pliku źródłowego: {source_path}")
                                            # Wypisz listę plików w katalogu dla debugowania
                                            if os.path.exists(comfyui_output_dir):
                                                files = os.listdir(comfyui_output_dir)
                                                logging.info(f"Dostępne pliki w {comfyui_output_dir}: {files}")
                        
                        if image_paths:
                            logging.info(f"Generacja zakończona, znaleziono i skopiowano {len(image_paths)} obrazów")
                            return image_paths
                
                # Jeśli nie znaleziono wyników, poczekaj i spróbuj ponownie
                logging.info(f"Generacja w toku, sprawdzanie ponownie za {polling_interval} sekund...")
                time.sleep(polling_interval)
                
            except Exception as e:
                logging.error(f"Błąd podczas sprawdzania statusu ComfyUI: {str(e)}")
                time.sleep(polling_interval)
        
        # Po upływie czasu zgłoś błąd timeout
        raise TimeoutError(f"Upłynął limit czasu oczekiwania na generację obrazów przez ComfyUI po {timeout} sekundach")

