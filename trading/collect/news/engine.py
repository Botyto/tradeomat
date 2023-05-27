import csv
from datetime import datetime
import io
import itertools
import os
import typing
from updateablezipfile import UpdateableZipFile
import zipfile

import collect.uid as uid

# Data storage description:
# data/news/yahoo/year-month.zip
# in each zip there's a csv file with the following columns:
# id, url, timestamp, title
# the text is stored in a separate file: <id>.txt

ROOT_DIR = os.path.join("data", "news")
INDEX_FILENAME = 'index.csv'


class NewsArticle:
    CSV_FIELDS = ["id", "url", "date", "title"]

    id: str|None = None
    url: str = None
    date: datetime = None
    title: str = None
    text: str = None


class NewsReader:
    namespace: str

    def __init__(self, namespace: str):
        self.namespace = namespace

    def _latest_zip(self):
        zips = os.listdir(os.path.join(ROOT_DIR, self.namespace))
        zips = [z for z in zips if z.endswith(".zip")]
        if zips:
            zips.sort()
            return zips[-1]

    def latest_date(self) -> datetime:
        latest_zip = self._latest_zip()
        if not latest_zip:
            return datetime.min
        latest_row = None
        zip_path = os.path.join(ROOT_DIR, self.namespace, latest_zip)
        with zipfile.ZipFile(zip_path, "r") as zip:
            with zip.open(INDEX_FILENAME, "r") as index_fh:
                reader = csv.DictReader(io.TextIOWrapper(index_fh, "utf-8"), NewsArticle.CSV_FIELDS)
                next(reader)  # skip header
                for row in reader:
                    if row["date"] > latest_row:
                        latest_row = row
        return latest_row["date"] if latest_row else datetime.min


class NewsWriter:
    namespace: str

    def __init__(self, namespace: str):
        self.namespace = namespace

    def _zip_path(self, date: datetime) -> str:
        return os.path.join(ROOT_DIR, self.namespace, f"{date.year:04}-{date.month:02}.zip")

    def _fixup_article(self, article: NewsArticle):
        assert article.date is not None
        if article.id is None:
            article.id = uid.new(article.date)

    def _article_fname(self, article: NewsArticle):
        return f"{article.id}.txt"

    def store(self, article: NewsArticle):
        self._fixup_article(article)
        zip_path = self._zip_path(article.date)
        zip_dir = os.path.dirname(zip_path)
        os.makedirs(zip_dir, exist_ok=True)
        with UpdateableZipFile(zip_path, "a", compression=zipfile.ZIP_LZMA) as zip:
            article_fname = self._article_fname(article)
            if article_fname in zip.namelist():
                raise ValueError(f"Article {article.id} already exists")
            index_data = []
            if INDEX_FILENAME in zip.namelist():
                with zip.open(INDEX_FILENAME, "r") as index_fh:
                    reader = csv.DictReader(io.TextIOWrapper(index_fh, "utf-8"), NewsArticle.CSV_FIELDS)
                    next(reader)  # skip header
                    index_data = list(reader)
            index_data.append({
                "id": article.id,
                "url": article.url,
                "date": article.date.isoformat(),
                "title": article.title,
            })
            index_content = io.StringIO()
            writer = csv.DictWriter(index_content, NewsArticle.CSV_FIELDS)
            writer.writeheader()
            writer.writerows(index_data)
            zip.writestr(INDEX_FILENAME, index_content.getvalue().encode("utf-8"))
            zip.writestr(article_fname, article.text)

    def store_many(self, articles: typing.List[NewsArticle]):
        for article in articles:
            self._fixup_article(article)
        by_zip = itertools.groupby(articles, lambda a: self._zip_path(a.date))
        for zip_path, zip_articles in by_zip:
            zip_dir = os.path.dirname(zip_path)
            os.makedirs(zip_dir, exist_ok=True)
            # TODO optimize
            for article in zip_articles:
                self.store(article)
