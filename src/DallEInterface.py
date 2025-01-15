import openai
import os


class DallEInterface():
    def __init__(self) -> None:
        # Configuration de l'API Azure OpenAI
        openai.api_type = "azure"
        openai.api_key = os.getenv("AZURE_OPENAI_DALLE_API_KEY")
        openai.azure_endpoint = os.getenv("AZURE_OPENAI_DALLE_ENDPOINT")
        openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

        # Nom du déploiement DALL-E sur Azure
        self.deployment_name: str = str(os.getenv("AZURE_OPENAI_DALLE_DEPLOYMENT_NAME"))

    def generate_image(self, prompt: str) -> openai.types.ImagesResponse:
        # Génération d'une image
        response = openai.images.generate(
            prompt=prompt,
            n=1,
            size="1024x1024",
            model=self.deployment_name
        )

        return response
