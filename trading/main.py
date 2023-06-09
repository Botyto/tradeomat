from collect.engine import Environment
env = Environment("../data", "../temp")

def collect_news():
    from collect.news.yahoo import YahooNewsCollector
    from collect.log import LogLevel

    c = YahooNewsCollector(env)
    c.log.level = LogLevel.DEBUG
    c.run_once()

def collect_countries():
    from collect.symbol.countries import PyCountryCollector

    c = PyCountryCollector(env)
    c.run_once()

def collect_stocks():
    from collect.symbol.secgov import SecGovCollector
    c = SecGovCollector(env)
    c.run_once()

def restore_news():
    import os
    import json
    from datetime import datetime, timezone
    from collect.news.engine import NewsArticle, NewsWriter
    from collect.news.yahoo import YahooNewsCollector

    src_dir = "D:/Workspace/datasets/yahoo news/news_articles_json"

    all_src_articles = []
    for fname in os.listdir(src_dir):
        print("at file", fname)
        file_path = os.path.join(src_dir, fname)
        with open(file_path, "rt", encoding="utf-8") as fh:
            src_data = json.load(fh)
            src_data = [
                {
                    **article,
                    "datetime": datetime.fromisoformat(article["datetime"]).replace(tzinfo=timezone.utc)
                }
                for article in src_data
            ]
            all_src_articles.extend(src_data)
    print("---------------------------------")
    print("total articles", len(all_src_articles))

    def month_of(a):
        dt = a["datetime"]
        return datetime(dt.year, dt.month, 1)

    all_src_articles.sort(key=month_of)
    def map(a: dict):
        for k in ["url", "datetime", "title", "body"]:
            if k not in a:
                return
        res = NewsArticle()
        res.url = a["url"]
        res.date = a["datetime"]
        res.title = a["title"]
        res.text = a["body"]
        return res
    print("remapping...")
    all_articles = [
        map(a)
        for a in all_src_articles
    ]
    all_articles = [a for a in all_articles if a]
    print("storing...")
    c = YahooNewsCollector(env)
    writer = NewsWriter(c, "yahoo")
    writer.store_many(all_articles)

def run_engine():
    import datetime

    import engine.engine
    import engine.data
    import engine.bar.yahoo as yahoo_bars

    data = engine.data.EventAggregator()
    feed_1 = yahoo_bars.make_feed("AAPL", yahoo_bars.YahooInterval.MIN_1)
    data.feeds.append(feed_1)
    feed_2 = yahoo_bars.make_feed("EURUSD=X", yahoo_bars.YahooInterval.MIN_1)
    data.feeds.append(feed_2)

    eng = engine.engine.Engine()
    eng.aggregator = data
    # eng.start_timestamp = datetime.datetime(2010, 1, 1, tzinfo=datetime.timezone.utc)
    # eng.end_timestamp = datetime.datetime(2017, 1, 1, tzinfo=datetime.timezone.utc)
    eng.start_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    task = eng.run()

collect_news()
# collect_stocks()
# restore_news()