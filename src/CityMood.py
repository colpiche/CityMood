import logging
from ast import Or
from DBManager import DBManager
from Orchestrator import *
from dotenv import load_dotenv

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,  # Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format des logs
    handlers=[
        logging.StreamHandler()  # Affichage des logs dans la console
    ]
)

# Chargement des variables d'environnement
load_dotenv()
logging.info("Variables d'environnement chargées.")

# Initialisation des interfaces et services
try:
    dalle_interface: DallEInterface = DallEInterface()
    logging.info("Interface DALL·E initialisée.")

    db: DBManager = DBManager('citymood')
    logging.info("Connexion à la base de données 'citymood' établie.")

    gpt_interface: GPTInterface = GPTInterface()
    logging.info("Interface GPT initialisée.")

    publisher: Publisher = Publisher(str(os.getenv("DISCORD_WEBHOOK")))
    logging.info("Publisher configuré avec le webhook Discord.")

    angou_scrap: Scrapper = Scrapper(
        [
            'https://www.charentelibre.fr/actualite/rss.xml',
            'https://www.nouvelle-aquitaine.fr/liste-rss/naq_actualite',
            'https://www.nouvelobs.com/festival-bd-angouleme/rss.xml',
            'https://www.francebleu.fr/rss/limousin/a-la-une.xml',
            'https://www.francebleu.fr/rss/la-rochelle/a-la-une.xml',
            'https://www.francebleu.fr/rss/perigord/a-la-une.xml'
        ],
        "Angoulême",
        db
    )
    logging.info("Scrapper initialisé avec les flux RSS d'Angoulême.")

    orchestrator: Orchestrator = Orchestrator(dalle_interface, db, gpt_interface, publisher, angou_scrap)
    logging.info("Orchestrator initialisé.")

except Exception as e:
    logging.error(f"Erreur lors de l'initialisation : {e}")
    raise

# Exécution principale
if __name__ == '__main__':
    try:
        logging.info("Début de l'exécution quotidienne.")

        orchestrator._daily_publish()
        logging.info("Publication quotidienne effectuée.")

        orchestrator.daily_routine()
        logging.info("Routine quotidienne effectuée.")

    except Exception as e:
        logging.error(f"Une erreur est survenue pendant l'exécution : {e}")
        raise

    finally:
        db.close()
        logging.info("Connexion à la base de données fermée.")