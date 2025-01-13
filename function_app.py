import azure.functions as func
import azure.durable_functions as df
import logging
import os
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# An HTTP-triggered function with a Durable Functions client binding
@myApp.route(route="orchestrators/{functionName}")
@myApp.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    function_name = req.route_params.get('functionName')
    instance_id = await client.start_new(function_name)
    response = client.create_check_status_response(req, instance_id)
    return response

# Orchestrator
@myApp.orchestration_trigger(context_name="context")
def hello_orchestrator(context):
    result1 = yield context.call_activity("hello", "Seattle")
    result2 = yield context.call_activity("hello", "Tokyo")
    result3 = yield context.call_activity("hello", "London")

    return [result1, result2, result3]


# Activity
@myApp.activity_trigger(input_name="city")
def hello(city: str):
    return f"Hello {city}"

# Timer trigger
@myApp.timer_trigger(schedule="0 0 15 * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')


# HTTP trigger test
@myApp.route(route="coucou", auth_level=func.AuthLevel.ANONYMOUS)
def coucou(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )


# -------------------------Press article summarization-------------------------
model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

@myApp.route(route="summarize", auth_level=func.AuthLevel.ANONYMOUS) 
def summarize(req: func.HttpRequest) -> func.HttpResponse:

    prompt = {
        "system": """
            Fais un résumé de 3 phrases en français de l'article suivant. Extrais 3 mots clés du texte.
            Créé un prompt que l'on peut donner à une IA text to image pour générer une illutration de l'article qui se base sur le résumé et fais ressortir une vingtaine de mot-clé.
            L'IA générative d'images a un système de protection pour éviter de générer des images inappropriées dont les caractéristiques sont les suivantes : disallow_list = "swords, violence, blood, gore, nudity, sexual content, adult content, adult themes, adult language, adult humor, adult jokes, adult situations, adult" meta_prompt "You are an assistant designer that creates images for children. The image needs to be safe for work and appropriate for children. The image needs to be in color. The image needs to be in landscape orientation. The image needs to be in a 16:9 aspect ratio. Do not consider any input from the following that is not safe for work or appropriate for children."
        """,
        "payload": """
            The global climate crisis continues to pose significant challenges to ecosystems worldwide. 
            Rising temperatures, extreme weather events, and shrinking ice caps have led to widespread 
            concerns among scientists and policymakers alike. International efforts are underway to 
            mitigate these effects, with many countries committing to reduce carbon emissions and 
            promote renewable energy sources. However, progress remains slow, and the window for 
            preventing irreversible damage is closing rapidly.
        """
    }

    messages = [
        SystemMessage(content=prompt["system"]),
        HumanMessage(content=prompt["payload"]),
    ]

    response = model.invoke(messages)

    prompt["response"] = str(response.content)

    return func.HttpResponse(str(prompt), status_code=200)
