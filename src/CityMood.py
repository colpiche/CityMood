from DBManager import Manager, DBArticle, DBPrompt, DBDay, DBTables
from datetime import datetime, timedelta, date
import random

db: Manager = Manager('citymood')

def insert_test_data():
    titles = [
        "The global climate crisis",
        "Advances in artificial intelligence",
        "Exploring the deep ocean",
        "Space exploration: the next frontier",
        "The rise of electric vehicles",
        "Breakthroughs in medical research",
        "The future of renewable energy",
        "Cybersecurity threats in 2025",
        "Cultural heritage in the digital age",
        "Blockchain and the financial revolution"
    ]

    descriptions = [
        "An urgent call to action on climate change.",
        "AI is changing the world at an unprecedented pace.",
        "Unveiling the mysteries of the ocean floor.",
        "Space exploration is expanding human horizons.",
        "Electric cars are revolutionizing transportation.",
        "New treatments and technologies are saving lives.",
        "Renewable energy is key to a sustainable future.",
        "Protecting data in an increasingly digital world.",
        "Preserving culture through digital innovation.",
        "How blockchain is disrupting traditional finance."
    ]

    urls = [f"https://example{index}.com/article/{index}" for index in range(1, 11)]

    contents = [
        '''Climate change continues to have widespread effects, and global cooperation is critical to mitigate its impact.''',
        '''Artificial intelligence is advancing rapidly, with significant implications for industry and society.''',
        '''Deep-sea exploration is revealing new species and geological phenomena previously unknown to science.''',
        '''Space missions are pushing the boundaries of what humans can achieve beyond Earth.''',
        '''Electric vehicles are becoming more accessible, with improved technology and charging infrastructure.''',
        '''Medical breakthroughs are improving life expectancy and quality of life across the globe.''',
        '''Solar, wind, and other renewable sources are gaining ground as viable alternatives to fossil fuels.''',
        '''Cybersecurity risks are evolving, and organizations are investing heavily in protective measures.''',
        '''Digital technologies are offering new ways to preserve and share cultural heritage worldwide.''',
        '''Blockchain is enabling new financial models, from cryptocurrencies to decentralized finance (DeFi).'''
    ]

    for i in range(10):
        # Générer une date aléatoire dans les 10 derniers jours avec une heure, minute et seconde aléatoires
        random_date = datetime.today() - timedelta(days=random.randint(0, 10))
        random_time = timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        publication_datetime = random_date + random_time

        db.insert_data(
            DBTables.ARTICLE,
            DBArticle(
                publication_date=publication_datetime,
                url=urls[i],
                title=titles[i],
                description=descriptions[i],
                content=contents[i]
            )
        )

if __name__ == '__main__':
    insert_test_data()
    articles = db.get_article_by_date(date(2025, 1, 9), datetime.strptime("02:00", "%H:%M"))
    db.close()