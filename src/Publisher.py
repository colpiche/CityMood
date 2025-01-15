import requests
import json

class Publisher():
    def __init__(self, discord_webhook: str) -> None:
        self._discord_webhook: str = discord_webhook
        pass

    def publish(self, message: str):
        self._publish_to_discord(self._discord_webhook, message)

    def _publish_to_discord(self, webhook: str, message: str) -> requests.Response:
        data = {"content": message}
        headers = {"Content-Type": "application/json"}
        response: requests.Response = requests.post(webhook, data=json.dumps(data), headers=headers)
        return response
