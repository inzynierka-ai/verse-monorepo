import os
import requests
from pathlib import Path
from app.core.config import settings
from app.services.image_generation.comfyui_service import ComfyUIService

# Dodaj ten fragment na początku test_simple.py aby sprawdzić URL
print(f"Adres ComfyUI: {settings.COMFYUI_API_URL}")

def check_server_availability():
    """Sprawdza czy serwer ComfyUI jest dostępny"""
    try:
        # Używamy podstawowego URL bez /api
        base_url = settings.COMFYUI_API_URL.split('/api')[0]
        response = requests.get(base_url)
        if response.status_code == 200:
            print("Serwer ComfyUI jest dostępny!")
            return True
        else:
            print(f"Serwer ComfyUI zwraca kod błędu: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Błąd połączenia z serwerem ComfyUI: {str(e)}")
        return False

def test_comfyui_service():
    # Sprawdź dostępność serwera
    if not check_server_availability():
        print("Test przerwany - serwer jest niedostępny")
        return

    # Inicjalizacja serwisu ComfyUI
    comfy_service = ComfyUIService()
    
    # Ścieżka do obrazka testowego
    image_path = Path(settings.MEDIA_ROOT) / "comfyui" / "reference_images" / "model_reference.jpg"
    
    # Sprawdź czy plik istnieje
    if not os.path.exists(image_path):
        print(f"BŁĄD: Plik {image_path} nie istnieje!")
        return
    
    print(f"Testowanie uploadowania obrazka: {image_path}")
    
    # Test 1: Upload obrazka
    uploaded_image = comfy_service.upload_image(str(image_path))
    
    if uploaded_image:
        print(f"SUKCES! Obrazek został pomyślnie załadowany do ComfyUI: {uploaded_image}")
        
        # Test 2: Pobranie danych obrazka dla workflow
        image_data = comfy_service.get_image_for_workflow(uploaded_image)
        print(f"Dane obrazka dla workflow: {image_data}")
        
        # Test 3: Sprawdzenie metody generate_with_reference (opcjonalnie)
        # Uwaga: To wymaga przygotowanego pliku workflow lub danych workflow
        # workflow_file = Path(settings.MEDIA_ROOT) / "comfyui" / "workflows" / "reference_workflow.json"
        # if os.path.exists(workflow_file):
        #    result = comfy_service.generate_with_reference(str(image_path), workflow_file=str(workflow_file))
        #    print(f"Wynik generowania: {result}")
        
    else:
        print("BŁĄD: Nie udało się załadować obrazka do ComfyUI")

if __name__ == "__main__":
    test_comfyui_service()