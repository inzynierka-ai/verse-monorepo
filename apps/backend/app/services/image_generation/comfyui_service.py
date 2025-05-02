import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from app.core.config import settings
from app.services.image_generation import WorkflowLoaderFactory


class ComfyUIService:
    def __init__(self):
        self.output_dir = Path(settings.MEDIA_ROOT) / "comfyui"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client_id = str(uuid.uuid4())
        # Define ComfyUI connection once
        self.comfy_url = settings.COMFYUI_API_URL

    def _queue_prompt(self, prompt: Dict[str, Any], client_id: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
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
            logging.error(
                f"Connection error getting image: {str(e)}. Check if ComfyUI is running at {self.comfy_url}")
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
            import time
            logging.info(
                f"Starting image generation for prompt: '{prompt}' (context: {context_type})")

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

            # Poll for job completion instead of using WebSockets
            max_wait_time = 300  # 5 minutes timeout
            start_time = time.time()
            poll_interval = 2  # Check every 2 seconds
            
            # Poll until job is complete or timeout occurs
            while time.time() - start_time < max_wait_time:
                # Check if the job is complete by getting history
                history = self._get_history(prompt_id)
                prompt_outputs = history.get(prompt_id, {}).get("outputs", {})
                
                if prompt_outputs:
                    logging.info(f"Generation complete after {int(time.time() - start_time)} seconds")
                    break
                    
                # Log progress periodically
                if int((time.time() - start_time) % 10) == 0:
                    logging.info(f"Still waiting for image generation... ({int(time.time() - start_time)}s elapsed)")
                
                # Wait before polling again
                time.sleep(poll_interval)
            else:
                # Loop completed without breaking - timeout occurred
                logging.error(f"Timeout waiting for image generation after {max_wait_time} seconds")
                return {"success": False, "error": "Timeout waiting for image generation", "imagePath": ""}

            logging.info(f"Generation complete, processing results")
            
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

    def generate_with_reference(self, reference_image_path, workflow_file=None, workflow_data=None):
        """
        Metoda do generowania obrazów z wykorzystaniem obrazka referencyjnego
        
        Args:
            reference_image_path (str): Ścieżka do pliku obrazka referencyjnego
            workflow_file (str, optional): Ścieżka do pliku workflow JSON dla ComfyUI
            workflow_data (dict, optional): Bezpośrednio podane dane workflow jako słownik
        
        Returns:
            dict: Słownik zawierający informacje o wyniku generowania
        """
        # 1. Upload obrazka referencyjnego
        uploaded_image = self.upload_image(reference_image_path)
        
        if not uploaded_image:
            logging.error("Nie udało się załadować obrazka referencyjnego. Przerywam generowanie.")
            return {"success": False, "error": "Nie udało się załadować obrazka referencyjnego"}
        
        # 2. Załaduj workflow z pliku JSON lub użyj podanych danych
        workflow = None
        if workflow_data:
            workflow = workflow_data
        elif workflow_file:
            try:
                with open(workflow_file, 'r') as f:
                    workflow = json.load(f)
            except Exception as e:
                logging.error(f"Błąd podczas ładowania workflow: {str(e)}")
                return {"success": False, "error": f"Błąd podczas ładowania workflow: {str(e)}"}
        else:
            logging.error("Nie podano ani pliku workflow, ani danych workflow")
            return {"success": False, "error": "Nie podano workflow"}
        
        # 3. Modyfikuj workflow, dodając referencję do załadowanego obrazka
        # Uwaga: Poniższy kod należy dostosować do konkretnego workflow
        # Znajdujemy wszystkie węzły typu "LoadImage"
        for node_id, node_data in workflow.get("nodes", {}).items():
            if node_data.get("class_type") == "LoadImage":
                # Dodajemy referencję do naszego obrazka
                node_data["inputs"]["image"] = self.get_image_for_workflow(uploaded_image)
        
        # 4. Wyślij workflow do przetworzenia
        try:
            # Używamy istniejącej metody _queue_prompt do wysłania workflow
            result = self._queue_prompt(workflow)
            
            if "prompt_id" in result:
                logging.info(f"Workflow został pomyślnie wysłany do ComfyUI z ID: {result['prompt_id']}")
                # Możemy użyć kodu z generate_image do oczekiwania na wynik i pobrania obrazka
                return {"success": True, "prompt_id": result["prompt_id"]}
            else:
                logging.error(f"Błąd podczas wysyłania workflow: {result}")
                return {"success": False, "error": "Błąd podczas wysyłania workflow"}
        except Exception as e:
            logging.error(f"Wystąpił błąd: {str(e)}")
            return {"success": False, "error": f"Wystąpił błąd: {str(e)}"}

    def upload_image(self, image_path):
        """
        Metoda do uploadowania obrazka referencyjnego do ComfyUI
        
        Args:
            image_path (str): Ścieżka do pliku obrazka
        
        Returns:
            str: Nazwa obrazka na serwerze ComfyUI lub None w przypadku błędu
        """
        # Sprawdzenie czy plik istnieje
        if not os.path.exists(image_path):
            logging.error(f"Plik {image_path} nie istnieje")
            return None
        
        try:
            # Odczytanie pliku obrazka
            with open(image_path, 'rb') as file:
                image_data = file.read()
            
            # Tworzenie nazwy pliku (używamy tylko nazwy bez ścieżki)
            filename = os.path.basename(image_path)
            
            # Przygotowanie danych do wysłania
            files = {
                'image': (filename, image_data)
            }
            
            # Endpoint do uploadowania obrazków w ComfyUI API - używamy self.comfy_url
            upload_url = f"{self.comfy_url}/upload/image"
            
            # Wysłanie żądania POST
            response = requests.post(upload_url, files=files)
            
            # Sprawdzenie odpowiedzi
            if response.status_code == 200:
                logging.info(f"Obrazek '{filename}' został pomyślnie załadowany do ComfyUI")
                return filename
            else:
                logging.error(f"Błąd podczas uploadowania obrazka: {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Wystąpił błąd podczas uploadowania obrazka: {str(e)}")
            return None

    def get_image_for_workflow(self, image_name):
        """
        Metoda zwracająca informacje o załadowanym obrazku dla workflow ComfyUI
        
        Args:
            image_name (str): Nazwa obrazka na serwerze
        
        Returns:
            dict: Dane obrazka w formacie wymaganym przez ComfyUI
        """
        return {
            "filename": image_name,
            "type": "input"
        }


def upload_image(image_path, comfy_server_address="http://127.0.0.1:8188"):
    """
    Funkcja do uploadowania obrazka referencyjnego do ComfyUI
    
    Args:
        image_path (str): Ścieżka do pliku obrazka
        comfy_server_address (str): Adres serwera ComfyUI
    
    Returns:
        str: Nazwa obrazka na serwerze ComfyUI lub None w przypadku błędu
    """
    # Sprawdzenie czy plik istnieje
    if not os.path.exists(image_path):
        print(f"Błąd: Plik {image_path} nie istnieje")
        return None
    
    try:
        # Odczytanie pliku obrazka
        with open(image_path, 'rb') as file:
            image_data = file.read()
        
        # Tworzenie nazwy pliku (używamy tylko nazwy bez ścieżki)
        filename = os.path.basename(image_path)
        
        # Przygotowanie danych do wysłania
        files = {
            'image': (filename, image_data)
        }
        
        # Endpoint do uploadowania obrazków w ComfyUI API
        upload_url = f"{comfy_server_address}/upload/image"
        
        # Wysłanie żądania POST
        response = requests.post(upload_url, files=files)
        
        # Sprawdzenie odpowiedzi
        if response.status_code == 200:
            print(f"Obrazek '{filename}' został pomyślnie załadowany do ComfyUI")
            return filename
        else:
            print(f"Błąd podczas uploadowania obrazka: {response.text}")
            return None
            
    except Exception as e:
        print(f"Wystąpił błąd: {str(e)}")
        return None
