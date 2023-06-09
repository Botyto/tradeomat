from collect.engine import Environment, BaseCollector
from datetime import timedelta

from collect.social.engine import SocialReader, SocialWriter
from collect.social.twitter_engine.scraper import TwitterScraper


class TwitterCollector(BaseCollector):
    reader: SocialReader
    writer: SocialWriter
    scraper: TwitterScraper
    username: str

    def __init__(self, env: Environment, username: str):
        super().__init__(env, timedelta(minutes=30))
        self.reader = SocialReader(env)
        self.writer = SocialWriter(env)
        self.scraper = TwitterScraper()
        self.username = username

    def run_once(self):
        latest_date = self.reader.latest_date(self.username)
        tweets = self.scraper.get_tweets(self.username, None, min_date=latest_date)
        self.writer.store_many(tweets)
