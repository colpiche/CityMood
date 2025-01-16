from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.utils.utils import convert_to_secret_str
import os
import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

class GPTInterface:
    def __init__(self) -> None:
        try:
            # Initialisation du modèle AzureChatOpenAI
            self._model: AzureChatOpenAI = AzureChatOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                api_key=convert_to_secret_str(str(os.getenv("AZURE_OPENAI_API_KEY")))
            )
            logging.info("GPTInterface initialisée avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation de GPTInterface : {e}")
            raise

    def ask(self, system_prompt: str, human_prompt: str) -> BaseMessage:
        try:
            logging.info(f"Envoi d'une requête au modèle avec les prompts : "
                         f"SystemPrompt='{system_prompt}' et HumanPrompt='{human_prompt}'")
            
            # Création des messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            # Envoi de la requête et récupération de la réponse
            response: BaseMessage = self._model.invoke(messages)
            
            logging.info("Réponse reçue avec succès.")
            return response
        except Exception as e:
            logging.error(f"Erreur lors de l'exécution de la méthode 'ask' : {e}")
            raise