from DBManager import Manager, DBArticle, DBTables
from datetime import datetime

def check_article_is_in_base_by_url(url:str, db: Manager) -> bool:
    if db.get_article_by_url(url) != []:
        return True
    else: 
        return False
    
def get_news(city:str, db: Manager, news_feed):
        cityPurged = city.lower()
        for entry in news_feed.entries:
            if check_article_is_in_base_by_url(entry.link, db):
                if ((city in entry.description) or (city in entry.title) or (city in entry.link) 
                    or (cityPurged in entry.description) or (cityPurged in entry.title) or (cityPurged in entry.link)):
                    print(f"Article {entry.title} n'est pas déjà dans la table")
                    db.insert_data(
                        DBTables.ARTICLE,
                        DBArticle(
                            publication_date=datetime.date.now,
                            url=entry.link,
                            title=entry.title,
                            description=entry.description,
                            content=""
                        )
                    )
