import openai
import os
import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("dalle_interface.log"),
        logging.StreamHandler()
    ]
)

class DallEInterface:
    def __init__(self) -> None:
        try:
            # Configuration de l'API Azure OpenAI
            openai.api_type = "azure"
            openai.api_key = os.getenv("AZURE_OPENAI_DALLE_API_KEY")
            openai.azure_endpoint = os.getenv("AZURE_OPENAI_DALLE_ENDPOINT")
            openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
            
            # Nom du déploiement DALL-E sur Azure
            self.deployment_name: str = str(os.getenv("AZURE_OPENAI_DALLE_DEPLOYMENT_NAME"))
            
            logging.info("DallEInterface initialisée avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation de DallEInterface : {e}")
            raise

    def generate_image(self, prompt: str) -> openai.types.ImagesResponse:
        try:
            logging.info(f"Demande de génération d'image avec le prompt : '{prompt}'")
            
            # Génération d'une image
            response = openai.images.generate(
                prompt=prompt,
                n=1,
                size="1024x1024",
                model=self.deployment_name
            )
            
            logging.info("Image générée avec succès.")
            return response
        except Exception as e:
            logging.error(f"Erreur lors de la génération d'image : {e}")
            raise