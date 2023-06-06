from collect.engine import Environment
env = Environment("../data", "../temp")

def collect_news():
    from collect.news.yahoo import YahooNewsCollector

    c = YahooNewsCollector(env)
    c.run_once()

def collect_countries():
    from collect.symbol.countries import PyCountryCollector

    c = PyCountryCollector(env)
    c.run_once()

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
