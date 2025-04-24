import requests
import os

def test_image_upload():
    # Ścieżka do obrazka testowego - dostosuj do swojej struktury folderów
    image_path = r"c:\Users\Marta\projekt\verse-monorepo\assets\reference_images\model_reference.jpg"
    
    # Sprawdź czy plik istnieje
    if not os.path.exists(image_path):
        print(f"BŁĄD: Plik {image_path} nie istnieje!")
        return
    
    # Adres API ComfyUI
    comfy_url = "http://127.0.0.1:8188/upload/image"
    
    try:
        # Przygotuj plik do wysłania
        filename = os.path.basename(image_path)
        files = {"image": (filename, open(image_path, "rb"))}
        
        print(f"Wysyłam plik: {filename} do ComfyUI...")
        
        # Wyślij żądanie
        response = requests.post(comfy_url, files=files)
        
        # Sprawdź wynik
        if response.status_code == 200:
            print("SUKCES! Obrazek został poprawnie przesłany do ComfyUI")
            print(f"Odpowiedź serwera: {response.text}")
        else:
            print(f"BŁĄD! Status: {response.status_code}")
            print(f"Treść odpowiedzi: {response.text}")
    
    except Exception as e:
        print(f"Wystąpił błąd: {str(e)}")

if __name__ == "__main__":
    test_image_upload()