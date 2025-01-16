from urllib.request import UnknownHandler
from DBManager import Manager, DBArticle, DBTables
from datetime import datetime, date
import feedparser

class Scrapper():
    def __init__(self, news_feeds_url: list[str], target_city: str, db: Manager) -> None:
        self._news_feeds_url = news_feeds_url
        self._city : str = target_city
        self._db : Manager = db
        pass
        
    def check_article_is_in_base_by_url(self, url:str, db: Manager) -> bool:
        '''
        Verifie que l'article n'est pas déjà dans la base 
        de donnée en retournant True ou False
        '''
        if db.get_article_by_url(url) != []:
            return True
        else: 
            return False
        
    def get_news(self, current_day_id: int):
        for news_feed_url in self._news_feeds_url:
            news_feed = feedparser.parse(news_feed_url)
            cityPurged = self._city.lower()
            for entry in news_feed.entries:
                if self.check_article_is_in_base_by_url(entry.link, self._db) == False:
                    if ((self._city in entry.description) or (self._city in entry.title) or (self._city in entry.link) 
                        or (cityPurged in entry.description) or (cityPurged in entry.title) or (cityPurged in entry.link)):
                        print(f"Article {entry.title} n'est pas déjà dans la table")
                        self._db.insert_data(
                            DBTables.ARTICLE,
                            DBArticle(
                                day_id = current_day_id,
                                publication_date=datetime.now(),
                                url=entry.link,
                                title=entry.title,
                                description=entry.description,
                                content=""
                            )
                        )
