import feedparser
import logging
from datetime import datetime
from DBManager import DBManager, DBArticle, DBTables

class Scrapper():
    def __init__(self, news_feeds_url: list[str], target_city: str, db: DBManager) -> None:
        self._news_feeds_url = news_feeds_url
        self._city: str = target_city
        self._db: DBManager = db

        # Configuration du logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler()
            ]
        )
        self._logger = logging.getLogger(__name__)

    def check_article_is_in_base_by_url(self, url: str, db: DBManager) -> bool:
        """
        Vérifie que l'article n'est pas déjà dans la base 
        de données en retournant True ou False.
        """
        if db.get_article_by_url(url) != []:
            self._logger.info(f"L'article {url} existe déjà dans la base de données.")
            return True
        else: 
            self._logger.info(f"L'article {url} n'est pas encore dans la base de données.")
            return False
        
    def get_news(self, current_day_id: int):
        for news_feed_url in self._news_feeds_url:
            try:
                self._logger.info(f"Récupération du flux RSS à partir de {news_feed_url}")
                news_feed = feedparser.parse(news_feed_url)
                cityPurged = self._city.lower()

                for entry in news_feed.entries:
                    if not ((self._city in entry.description) or 
                        (self._city in entry.title) or 
                        (self._city in entry.link) or 
                        (cityPurged in entry.description) or 
                        (cityPurged in entry.title) or 
                        (cityPurged in entry.link)):
                        self._logger.info(f"Article '{entry.title}' ne concerne pas {self._city}. Ignoré.")
                        continue
                        # Vérification si l'article concerne la ville cible
                    if self.check_article_is_in_base_by_url(entry.link, self._db) == False:
                        
                        self._logger.info(f"Article '{entry.title}' n'est pas encore dans la base. Ajout à la base de données.")
                        self._db.insert_data(
                            DBTables.ARTICLE,
                            DBArticle(
                                day_id=current_day_id,
                                publication_date=datetime.now(),
                                url=entry.link,
                                title=entry.title,
                                description=entry.description,
                                content=""
                            )
                        )
            except Exception as e:
                # Log en cas d'erreur lors du traitement du flux RSS
                self._logger.error(f"Erreur lors de la récupération du flux RSS depuis {news_feed_url}: {str(e)}")

