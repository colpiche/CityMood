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
    # insert_test_data()
    # articles = db.get_article_by_date(date(2025, 1, 9), datetime.strptime("02:00", "%H:%M"))
    orchestrator.daily_publish()
    db.close()
