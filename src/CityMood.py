from ast import Or
from DBManager import Manager
from Orchestrator import *
from dotenv import load_dotenv

load_dotenv()

dalle_interface : DallEInterface = DallEInterface()

db: Manager = Manager('citymood')

gpt_interface : GPTInterface = GPTInterface()

publisher : Publisher = Publisher("https://discord.com/api/webhooks/1329063802205110407/2NbBEacCLp8H-21YU0eVUldCWvKsWBFKZRVEyFdvc9UAiFGz0tCTrTRjsI_EtLUO-nwh")

allscrap : list[Scrapper] = []
angou_scrap : Scrapper = Scrapper('https://www.charentelibre.fr/actualite/rss.xml', "Angoulême", db)
allscrap.append(angou_scrap)
angou_scrap2 : Scrapper = Scrapper('https://www.nouvelle-aquitaine.fr/liste-rss/naq_actualite', "Angoulême", db)
allscrap.append(angou_scrap2)
angou_scrap3 : Scrapper = Scrapper('https://www.nouvelobs.com/festival-bd-angouleme/rss.xml', "Angoulême", db)
allscrap.append(angou_scrap3)
angou_scrap4 : Scrapper = Scrapper('https://www.francebleu.fr/rss/limousin/a-la-une.xml', "Angoulême", db)
allscrap.append(angou_scrap4)
angou_scrap5 : Scrapper = Scrapper('https://www.francebleu.fr/rss/la-rochelle/a-la-une.xml', "Angoulême", db)
allscrap.append(angou_scrap5)
angou_scrap6 : Scrapper = Scrapper('https://www.francebleu.fr/rss/perigord/a-la-une.xml', "Angoulême", db)
allscrap.append(angou_scrap6)

orchestrator : Orchestrator = Orchestrator(dalle_interface, db, gpt_interface, publisher, [angou_scrap,angou_scrap2])

if __name__ == '__main__':
    orchestrator._daily_publish()
    orchestrator.daily_routine()
    db.close()
