import requests
import os
import base64
import json

def upload_image_to_comfy(image_path, comfy_server_address="http://127.0.0.1:8188"):
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

def get_image_for_workflow(image_name, comfy_server_address="http://127.0.0.1:8188"):
    """
    Funkcja zwracająca informacje o załadowanym obrazku dla workflow ComfyUI
    
    Args:
        image_name (str): Nazwa obrazka na serwerze
        comfy_server_address (str): Adres serwera ComfyUI
    
    Returns:
        dict: Dane obrazka w formacie wymaganym przez ComfyUI
    """
    return {
        "filename": image_name,
        "type": "input"
    }

if __name__ == "__main__":
    # Ścieżka do obrazka referencyjnego (dostosuj według potrzeb)
    reference_image_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "assets", "reference_images", "model_reference.jpg"
    )
    
    # Adres serwera ComfyUI (dostosuj według potrzeb)
    comfy_address = "http://127.0.0.1:8188"
    
    # Upload obrazka
    uploaded_image = upload_image_to_comfy(reference_image_path, comfy_address)
    
    if uploaded_image:
        # Pobierz dane obrazka dla workflow
        image_data = get_image_for_workflow(uploaded_image, comfy_address)
        print(f"Dane obrazka do użycia w workflow: {json.dumps(image_data, indent=2)}")