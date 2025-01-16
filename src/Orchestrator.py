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
                    publisher: Publisher, scrappers: list[Scrapper]) -> None:
        self._dallEInterface = dallEInterface
        self._db = db
        self._gptinterface = gptinterface
        self._publisher = publisher
        self._scrappers = scrappers
        self._id_current_day = self._db.get_day_id_by_date(date.today())
        print(self._id_current_day)
        pass
    
    # def insert_test_data(self) -> None:
    #     titles = [
    #         "The global climate crisis",
    #         "Advances in artificial intelligence",
    #         "Exploring the deep ocean",
    #         "Space exploration: the next frontier",
    #         "The rise of electric vehicles",
    #         "Breakthroughs in medical research",
    #         "The future of renewable energy",
    #         "Cybersecurity threats in 2025",
    #         "Cultural heritage in the digital age",
    #         "Blockchain and the financial revolution"
    #     ]

    #     descriptions = [
    #         "An urgent call to action on climate change.",
    #         "AI is changing the world at an unprecedented pace.",
    #         "Unveiling the mysteries of the ocean floor.",
    #         "Space exploration is expanding human horizons.",
    #         "Electric cars are revolutionizing transportation.",
    #         "New treatments and technologies are saving lives.",
    #         "Renewable energy is key to a sustainable future.",
    #         "Protecting data in an increasingly digital world.",
    #         "Preserving culture through digital innovation.",
    #         "How blockchain is disrupting traditional finance."
    #     ]

    #     urls = [f"https://example{index}.com/article/{index}" for index in range(1, 11)]

    #     contents = [
    #         '''Climate change continues to have widespread effects, and global cooperation is critical to mitigate its impact.''',
    #         '''Artificial intelligence is advancing rapidly, with significant implications for industry and society.''',
    #         '''Deep-sea exploration is revealing new species and geological phenomena previously unknown to science.''',
    #         '''Space missions are pushing the boundaries of what humans can achieve beyond Earth.''',
    #         '''Electric vehicles are becoming more accessible, with improved technology and charging infrastructure.''',
    #         '''Medical breakthroughs are improving life expectancy and quality of life across the globe.''',
    #         '''Solar, wind, and other renewable sources are gaining ground as viable alternatives to fossil fuels.''',
    #         '''Cybersecurity risks are evolving, and organizations are investing heavily in protective measures.''',
    #         '''Digital technologies are offering new ways to preserve and share cultural heritage worldwide.''',
    #         '''Blockchain is enabling new financial models, from cryptocurrencies to decentralized finance (DeFi).'''
    #     ]

    #     for i in range(10):
    #         # Générer une date aléatoire dans les 10 derniers jours avec une heure, minute et seconde aléatoires
    #         random_date = datetime.today() - timedelta(days=random.randint(0, 10))
    #         random_time = timedelta(
    #             hours=random.randint(0, 23),
    #             minutes=random.randint(0, 59),
    #             seconds=random.randint(0, 59)
    #         )
    #         publication_datetime = random_date + random_time

    #         self._db.insert_data(
    #             DBTables.ARTICLE,
    #             DBArticle(
    #                 publication_date=publication_datetime,
    #                 url=urls[i],
    #                 title=titles[i],
    #                 description=descriptions[i],
    #                 content=contents[i]
    #             )
    #         )
            
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
        for scrapper in self._scrappers:
            scrapper.get_news(self._id_current_day)
        
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
            liens = liens + article["title"] + "\n"
        # articles_of_the_day: list[DBArticle]= self._db.get_article_by_date((datetime.now() + timedelta(days=1)))
        prompt = self._insert_daily_prompt(articles_of_the_day)
        self._publisher.publish(message = "Les articles d'Angoulême du jours :\n " +
                                liens +
                                prompt['image_url'])
        
        
    def daily_routine(self):
        schedule.every(10).minutes.do(self._get_angouleme_s_news)
        schedule.every().day.at("20:00").do(self._daily_publish)

        while True:
            schedule.run_pending()