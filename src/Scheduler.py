from apscheduler.schedulers.blocking import BlockingScheduler 
from Scrapper import *
from DBManager import Manager


def check_news_feed_every_ten_minutes(city:str, db: Manager, news_feed):
    scheduler = BlockingScheduler() 
    # Schedule the job to run every minute 
    scheduler.add_job(get_news(city, db, news_feed), 'interval', minutes=1) 
    
    try: 
        scheduler.start() 
    except (KeyboardInterrupt, SystemExit): 
        pass 
