from datetime import datetime, timedelta, timezone
import requests
import time
import typing

from collect.news.engine import NewsReader, NewsWriter, NewsArticle

NAMESPACE = "yahoo"


class YahooHomepageScraper:
    def scrape(self, homepage_html: str) -> typing.List[NewsArticle]:
        return []


class YahooNewsScraper:
    LIVE_TOLERANCE = timedelta(minutes=5)

    reader: NewsReader
    writer: NewsWriter
    scraper: YahooHomepageScraper

    def __init__(self):
        self.reader = NewsReader(NAMESPACE)
        self.writer = NewsWriter(NAMESPACE)
        self.scraper = YahooHomepageScraper()

    def _collect_history(self, start: datetime, end: datetime):
        pass  # TODO scrape using wayback machine

    def _collect_live(self):
        response = requests.get("https://finance.yahoo.com/")
        response.raise_for_status()
        articles = self.scraper.scrape(response.text)
        self.writer.store_many(articles)

    def _collect_since(self, since: datetime):
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        if now - since > self.LIVE_TOLERANCE:
            self._collect_history(since, now - self.LIVE_TOLERANCE)
        self._collect_live()

    def run_forever(self):
        while True:
            latest_date = self.reader.latest_date()
            self._collect_since(latest_date)
            time.sleep(self.LIVE_TOLERANCE.total_seconds() - 1.0)
