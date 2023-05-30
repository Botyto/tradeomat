import bs4
from datetime import datetime, timedelta, timezone
import requests
import typing

from collect.engine import BaseCollector
from collect.news.engine import NewsReader, NewsWriter, NewsArticle
from collect.wayback import WaybackScraper
from collect.web import HttpClient

NAMESPACE = "yahoo"


class YahooArticleScraper:
    client: HttpClient

    def __init__(self, client: HttpClient|None = None):
        self.client = client or HttpClient()

    def _get_article_urls(self, homepage_html: str) -> typing.Set[str]:
        try:
            soup = bs4.BeautifulSoup(homepage_html, "html.parser")
        except:
            return set()
        article_urls = set()
        for a in soup.find_all('a'):
            try:
                href = a["href"]
                if not isinstance(href, str) or not href.endswith(".html"):
                    continue
                full_url = None
                if href.startswith("/news/"):
                    full_url = "https://finance.yahoo.com" + href
                elif href.startswith("https://finance.yahoo.com/news/"):
                    full_url = href
                elif href.startswith("finance.yahoo.com/news/"):
                    full_url = "https://" + href
                if not full_url:
                    continue
                article_urls.add(full_url)
            except:
                pass
        return article_urls

    def _parse_article_date(datetime_str: str) -> datetime|None:
        formats = [
            "%B %d, %Y",
            "%B %d, %Y at %I:%M %p",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                pass

    def _prase_article(self, article_html: str) -> NewsArticle:
        result = NewsArticle()
        soup = bs4.BeautifulSoup(article_html, "html.parser")
        header_div = soup.find("div", {"class": "caas-title-wrapper"})
        if header_div:
            result.title = header_div.text.strip()
        # author_div = soup.find("div", {"class": "caas-author-byline-collapse"})
        # if author_div:
        #     result["author"] = author_div.text.strip()
        datetime_div = soup.find("div", {"class": "caas-attr-time-style"})
        if datetime_div:
            datetime_str = datetime_div.find("time").text.strip()
            posted_datetime = self._parse_article_date(datetime_str)
            if posted_datetime:
                result.date = posted_datetime
        body_paragraphs = []
        body_div = soup.find("div", {"class": "caas-body"})
        for body_p in body_div.find_all("p"):
            body_paragraphs.append(body_p.text.strip())
        if body_paragraphs:
            result.text = "\n".join(body_paragraphs)
        # links = []
        # for body_a in body_div.find_all("a"):
        #     links.append(body_a.get("href"))
        return result

    def _get_article(self, article_url: str) -> NewsArticle:
        response = self.client.get(article_url)
        response.raise_for_status()
        article_html = response.text
        article = self._prase_article(article_html)
        article.url = article_url
        return article

    def scrape(self, homepage_html: str) -> typing.List[NewsArticle]:
        article_urls = self._get_article_urls(homepage_html)
        return [self._get_article(url) for url in article_urls]


class YahooNewsCollector(BaseCollector):
    HOMEPAGE_URL = "https://finance.yahoo.com/"
    LIVE_TOLERANCE = timedelta(minutes=5)

    reader: NewsReader
    writer: NewsWriter
    scraper: YahooArticleScraper
    wayback: WaybackScraper

    def __init__(self):
        super().__init__(self.LIVE_TOLERANCE)
        self.reader = NewsReader(NAMESPACE)
        self.writer = NewsWriter(NAMESPACE)
        self.scraper = YahooArticleScraper()
        self.wayback = WaybackScraper()

    def _collect_history(self, start: datetime, end: datetime):
        snapshots = self.wayback.list_snapshopts(self.HOMEPAGE_URL, start, end)
        articles = self.wayback.for_each(snapshots, self.scraper.scrape)
        self.writer.store_many(articles)

    def _collect_live(self):
        response = requests.get(self.HOMEPAGE_URL)
        response.raise_for_status()
        articles = self.scraper.scrape(response.text)
        self.writer.store_many(articles)

    def _collect_since(self, since: datetime):
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        if now - since > self.LIVE_TOLERANCE:
            self._collect_history(since, now - self.LIVE_TOLERANCE)
        self._collect_live()

    def run_once(self):
        latest_date = self.reader.latest_date()
        self._collect_since(latest_date)
