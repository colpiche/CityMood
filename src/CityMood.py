from ast import Or
from DBManager import Manager
from Orchestrator import *
from dotenv import load_dotenv

load_dotenv()

dalle_interface : DallEInterface = DallEInterface()

db: Manager = Manager('citymood')

gpt_interface : GPTInterface = GPTInterface()

publisher : Publisher = Publisher("https://discord.com/api/webhooks/1329063802205110407/2NbBEacCLp8H-21YU0eVUldCWvKsWBFKZRVEyFdvc9UAiFGz0tCTrTRjsI_EtLUO-nwh")

angou_scrap : Scrapper = Scrapper('https://www.charentelibre.fr/actualite/rss.xml', "Angoulême", db)

orchestrator : Orchestrator = Orchestrator(dalle_interface, db, gpt_interface, publisher, angou_scrap)

if __name__ == '__main__':
    orchestrator._daily_publish()
    orchestrator.daily_routine()
    db.close()
