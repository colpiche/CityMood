import requests
import json
import logging

class Publisher():
    def __init__(self, discord_webhook: str) -> None:
        self._discord_webhook: str = discord_webhook
        # Configuration du logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self._logger = logging.getLogger(__name__)

    def publish(self, message: str) -> bool:
        """Publie un message sur Discord via le webhook."""
        try:
            response = self._publish_to_discord(self._discord_webhook, message)
            if response.status_code == 204:  # Discord retourne un code 204 si tout va bien
                self._logger.info("Message publié avec succès.")
                return True
            else:
                self._logger.warning(
                    "Échec de la publication : Code HTTP %d, Réponse : %s",
                    response.status_code,
                    response.text
                )
                return False
        except requests.RequestException as e:
            self._logger.error("Erreur lors de l'envoi du message : %s", str(e))
            return False

    def _publish_to_discord(self, webhook: str, message: str) -> requests.Response:
        """Envoie le message au webhook Discord."""
        data = {"content": message}
        headers = {"Content-Type": "application/json"}
        response: requests.Response = requests.post(webhook, data=json.dumps(data), headers=headers)
        return response
