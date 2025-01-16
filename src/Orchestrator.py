from datetime import date, datetime, timedelta
from os import link
from DallEInterface import *
from DBManager import *
from GPTInterface import *
from Publisher import *
from Scrapper import *
import random
import schedule

class Orchestrator():
    def __init__(self, dallEInterface: DallEInterface, db:Manager, gptinterface: GPTInterface,
                    publisher: Publisher, scrapper: Scrapper) -> None:
        self._dallEInterface = dallEInterface
        self._db = db
        self._gptinterface = gptinterface
        self._publisher = publisher
        self._scrappers = scrapper
        self._id_current_day = self._db.get_day_id_by_date(date.today())
        print(self._id_current_day)
        pass
 
    def serialize_articles(self, articles: list[DBArticle]) -> str:
        """
        Sérialise une liste de DBArticle en JSON avec uniquement les champs title, description et content.
        
        :param articles: Liste d'articles de type DBArticle.
        :return: Chaîne JSON contenant uniquement les champs sélectionnés.
        """
        filtered_articles = [
            {
                'title': article['title'],
                'description': article['description'],
                'content': article['content']
            }
            for article in articles
        ]
        
        return json.dumps(filtered_articles, ensure_ascii=False, separators=(',', ':'))

    def _get_angouleme_s_news(self) -> None:
        self._scrappers.get_news(self._id_current_day)
        
    def _insert_daily_prompt(self, articles_of_the_day: list[DBArticle]) -> DBPrompt:
        painting_description: str = str(self._gptinterface.ask("Décris moi un tableau qui aurait été peint par un artiste dans un style réaliste suite à sa lecture de ces articles", self.serialize_articles(articles_of_the_day)).content)
        dall_e_url = self._dallEInterface.generate_image(painting_description)
        daily_prompt: DBPrompt = DBPrompt(day_id=self._id_current_day, text_used = painting_description, image_url = str(dall_e_url.data[0].url))
        daily_prompt["id"] = self._db.insert_data(DBTables.PROMPT, daily_prompt)
        return daily_prompt
     
    def _update_day_id(self) ->  None:
        self._id_current_day = self._db.get_day_id_by_date(date.today() + timedelta(days=1))
        
    def _daily_publish(self) -> None:
        self._get_angouleme_s_news()
        articles_of_the_day: list[DBArticle]= self._db.get_article_by_date(self._id_current_day)
        liens: str = ""
        for article in articles_of_the_day:
            liens = liens + "*" + article["title"] + "*" + "\n"
        # articles_of_the_day: list[DBArticle]= self._db.get_article_by_date((datetime.now() + timedelta(days=1)))
        prompt = self._insert_daily_prompt(articles_of_the_day)
        
        self._publisher.publish(title = "Les articles d'Angoulême du jour :",
                                message = liens,
                                url = prompt['image_url'])
        
    def daily_routine(self):
        schedule.every(10).minutes.do(self._get_angouleme_s_news)
        schedule.every().day.at("20:00").do(self._daily_publish)

        while True:
            schedule.run_pending()