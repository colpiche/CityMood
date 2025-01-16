from datetime import date, datetime, timedelta
from os import link
from DallEInterface import *
from DBManager import *
from GPTInterface import *
from Publisher import *
from Scrapper import *
import schedule
import logging
import json
import time

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

class Orchestrator:
    def __init__(self, dallEInterface: DallEInterface, db: Manager, gptinterface: GPTInterface,
                 publisher: Publisher, scrapper: Scrapper) -> None:
        try:
            self._dallEInterface = dallEInterface
            self._db = db
            self._gptinterface = gptinterface
            self._publisher = publisher
            self._scrappers = scrapper
            self._id_current_day = self._db.get_day_id_by_date(date.today())
            logging.info(f"Orchestrator initialisé avec day_id : {self._id_current_day}")
        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation de l'Orchestrator : {e}")
            raise

    def serialize_articles(self, articles: list[DBArticle]) -> str:
        """
        Sérialise une liste de DBArticle en JSON avec uniquement les champs title, description et content.
        
        :param articles: Liste d'articles de type DBArticle.
        :return: Chaîne JSON contenant uniquement les champs sélectionnés.
        """
        try:
            filtered_articles = [
                {
                    'title': article['title'],
                    'description': article['description'],
                    'content': article['content']
                }
                for article in articles
            ]
            serialized = json.dumps(filtered_articles, ensure_ascii=False, separators=(',', ':'))
            logging.info("Articles sérialisés avec succès.")
            return serialized
        except Exception as e:
            logging.error(f"Erreur lors de la sérialisation des articles : {e}")
            raise

    def _get_angouleme_s_news(self) -> None:
        try:
            logging.info("Récupération des actualités d'Angoulême...")
            self._scrappers.get_news(self._id_current_day)
            logging.info("Actualités récupérées avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des actualités : {e}")
            raise

    def _insert_daily_prompt(self, articles_of_the_day: list[DBArticle]) -> DBPrompt:
        try:
            logging.info("Insertion du daily prompt...")
            
            # Génération de la description de l'image
            painting_description: str = str(self._gptinterface.ask(
                "Décris moi un tableau qui aurait été peint par un artiste dans un style réaliste suite à sa lecture de ces articles, il ne doit pas représenter de la violence",
                self.serialize_articles(articles_of_the_day)).content)

            # Tentative de génération d'image avec Dall-E
            attempts = 0
            max_attempts = 5  # Limiter à 5 tentatives pour éviter une boucle infinie

            while attempts < max_attempts:
                try:
                    dall_e_url = self._dallEInterface.generate_image(painting_description)
                    daily_prompt: DBPrompt = DBPrompt(
                        day_id=self._id_current_day, 
                        text_used=painting_description, 
                        image_url=str(dall_e_url.data[0].url)
                    )
                    daily_prompt["id"] = self._db.insert_data(DBTables.PROMPT, daily_prompt)
                    logging.info("Daily prompt inséré avec succès.")
                    return daily_prompt  # Retourner dès que l'image est générée avec succès

                except Exception as e:
                    # Si l'API Dall-E échoue (par exemple, si le prompt est invalide)
                    logging.warning(f"Échec de la génération de l'image avec le prompt : {painting_description}. Tentative #{attempts + 1}...")
                    attempts += 1
                    time.sleep(2)  # Attendre 2 secondes avant de réessayer, pour éviter un spam de requêtes

            # Si après plusieurs tentatives l'image ne peut toujours pas être générée
            logging.error("Impossible de générer une image après plusieurs tentatives.")
            raise Exception("Échec de génération d'image après plusieurs tentatives.")
        
        except Exception as e:
            logging.error(f"Erreur lors de l'insertion du daily prompt : {e}")
            raise

    def _update_day_id(self) -> None:
        try:
            logging.info("Mise à jour de l'id du jour...")
            self._id_current_day = self._db.get_day_id_by_date(date.today() + timedelta(days=1))
            logging.info(f"Id du jour mis à jour : {self._id_current_day}")
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour de l'id du jour : {e}")
            raise

    def _daily_publish(self) -> None:
        try:
            logging.info("Début de la publication quotidienne...")
            self._get_angouleme_s_news()
            articles_of_the_day: list[DBArticle] = self._db.get_article_by_date(self._id_current_day)
            
            liens: str = ""
            for article in articles_of_the_day:
                liens += f"*{article['title']}*\n"
            
            prompt = self._insert_daily_prompt(articles_of_the_day)
            
            self._publisher.publish(
                title="Les articles d'Angoulême du jour :",
                message=liens,
                url=prompt['image_url']
            )
            logging.info("Publication quotidienne effectuée avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors de la publication quotidienne : {e}")
            raise

    def daily_routine(self):
        try:
            logging.info("Configuration de la routine quotidienne...")
            schedule.every(10).minutes.do(self._get_angouleme_s_news)
            schedule.every().day.at("20:00").do(self._daily_publish)

            logging.info("Routine quotidienne configurée. Démarrage...")
            while True:
                schedule.run_pending()
        except Exception as e:
            logging.error(f"Erreur dans la routine quotidienne : {e}")
            raise