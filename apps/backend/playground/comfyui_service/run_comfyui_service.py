from app.services.image_generation.comfyui_service import ComfyUIService

def test_comfyui_service():
    comfyui_service = ComfyUIService()
    image_path = comfyui_service.generate_image("young dark hair police officer")
    print(f"Image path: {image_path}")

if __name__ == "__main__":
    test_comfyui_service()