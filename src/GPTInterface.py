from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.utils.utils import convert_to_secret_str
import os

class GPTInterface():
    def __init__(self) -> None:
        self._model: AzureChatOpenAI = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=convert_to_secret_str(str(os.getenv("AZURE_OPENAI_API_KEY")))
        )
    
    def ask(self, system_prompt: str, human_prompt: str) -> BaseMessage:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]

        response: BaseMessage = self._model.invoke(messages)

        return response
