import azure.functions as func
import azure.durable_functions as df
import logging
import feedparser
import unidecode

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

news_feed = feedparser.parse('https://www.charentelibre.fr/actualite/rss.xml')

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
    
@myApp.route(route="GetNews", auth_level=func.AuthLevel.ANONYMOUS)
@myApp.timer_trigger(schedule="0 0 15 * * *", arg_name="GetNews", run_on_startup=True,
              use_monitor=False) 
def GetNews(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed the request TestRss.')

    city = req.params.get('city')
    if not city:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            city = req_body.get('city')

    if city:
        cityPurged = unidecode.unidecode(city).lower()
        result = ""
        for entry in news_feed.entries:
            if ((city in entry.description) or (city in entry.title) or (city in entry.link)):
                result += entry.title + "\n"
            elif ((cityPurged in entry.description) or (cityPurged in entry.title) or (cityPurged in entry.link)):
                result += entry.title + "\n"
        return func.HttpResponse(result)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )