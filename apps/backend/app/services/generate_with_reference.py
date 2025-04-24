from upload_reference import upload_image_to_comfy, get_image_for_workflow
import requests
import json
import os

def generate_with_reference(reference_image_path, workflow_file, comfy_server_address="http://127.0.0.1:8188"):
    """
    Funkcja do generowania obrazów z wykorzystaniem obrazka referencyjnego
    
    Args:
        reference_image_path (str): Ścieżka do pliku obrazka referencyjnego
        workflow_file (str): Ścieżka do pliku workflow JSON dla ComfyUI
        comfy_server_address (str): Adres serwera ComfyUI
    """
    # 1. Upload obrazka referencyjnego
    uploaded_image = upload_image_to_comfy(reference_image_path, comfy_server_address)
    
    if not uploaded_image:
        print("Nie udało się załadować obrazka referencyjnego. Przerywam generowanie.")
        return
    
    # 2. Załaduj workflow z pliku JSON
    try:
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
    except Exception as e:
        print(f"Błąd podczas ładowania workflow: {str(e)}")
        return
    
    # 3. Modyfikuj workflow, dodając referencję do załadowanego obrazka
    # Uwaga: Poniższy kod należy dostosować do konkretnego workflow
    # Zakładamy, że w workflow istnieje węzeł typu "LoadImage" o ID "node_1"
    if "node_1" in workflow["nodes"]:
        workflow["nodes"]["node_1"]["inputs"]["image"] = get_image_for_workflow(uploaded_image)
    
    # 4. Wyślij workflow do ComfyUI API
    try:
        api_endpoint = f"{comfy_server_address}/api/queue"
        response = requests.post(
            api_endpoint, 
            json={"workflow": workflow}
        )
        
        if response.status_code == 200:
            print("Workflow został pomyślnie wysłany do ComfyUI")
            print(f"ID zadania: {response.json().get('prompt_id')}")
        else:
            print(f"Błąd podczas wysyłania workflow: {response.text}")
    except Exception as e:
        print(f"Wystąpił błąd: {str(e)}")

# Przykład użycia
if __name__ == "__main__":
    reference_image_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "assets", "reference_images", "model_reference.jpg"
    )
    
    workflow_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "workflows", "my_workflow.json"
    )
    
    generate_with_reference(reference_image_path, workflow_file)