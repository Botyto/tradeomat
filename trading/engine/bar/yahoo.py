from datetime import datetime, timedelta, timezone
from enum import Enum
import requests

from engine.bar.event import BarEvent
from engine.bar.feed import BarFeed
from engine.bar.history import CsvBarHistory, CsvColumnMapping
from engine.bar.live import BarLiveFeed

YAHOO_CSV_COLUMNS = [
    CsvColumnMapping("Date", lambda x: datetime.strptime(x, "%Y-%m-%d").replace(tzinfo=timezone.utc), "timestamp"),
    CsvColumnMapping("Open", float, "open"),
    CsvColumnMapping("High", float, "high"),
    CsvColumnMapping("Low", float, "low"),
    CsvColumnMapping("Close", float, "close"),
    CsvColumnMapping("Volume", float, "volume"),
]


class YahooInterval(Enum):
    MIN_1 = "1m"
    MIN_5 = "5m"
    HOUR_1 = "1h"
    DAY_1 = "1d"
    DAY_5 = "5d"
    MONTH_1 = "1mo"
    MONTH_3 = "3mo"
    MONTH_5 = "5mo"
    YEAR_1 = "1y"
    YEAR_2 = "2y"
    YEAR_5 = "5y"
    YEAR_10 = "10y"

YAHOO_INTERVAL_TO_DELTA = {
    YahooInterval.MIN_1: timedelta(minutes=1),
    YahooInterval.MIN_5: timedelta(minutes=5),
    YahooInterval.HOUR_1: timedelta(hours=1),
    YahooInterval.DAY_1: timedelta(days=1),
    YahooInterval.DAY_5: timedelta(days=5),
    YahooInterval.MONTH_1: timedelta(days=30),
    YahooInterval.MONTH_3: timedelta(days=90),
    YahooInterval.MONTH_5: timedelta(days=150),
    YahooInterval.YEAR_1: timedelta(days=365),
    YahooInterval.YEAR_2: timedelta(days=365*2),
    YahooInterval.YEAR_5: timedelta(days=365*5),
    YahooInterval.YEAR_10: timedelta(days=365*10),
}


class YahooLiveFeed(BarLiveFeed):
    HEADERS = {
        "User-Agent": "Mozilla/5.0",
    }

    interval_str: str

    def __init__(self, ticker: str, interval: YahooInterval):
        super().__init__(ticker, YAHOO_INTERVAL_TO_DELTA[interval])
        self.interval_str = interval.value

    async def _fetch(self, target: datetime) -> BarEvent:
        target_timestamp = int(target.timestamp())
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{self.ticker}?" + \
            f"lang=en-US&" + \
            f"region=US&" + \
            f"includeAdjustedClose=true&" + \
            f"interval={self.interval_str}&" + \
            f"period1={target_timestamp}&" + \
            f"period2={target_timestamp + 59}&" + \
            f"events=capitalGain%7Cdiv%7Csplit&" + \
            f"useYfid=true&" + \
            f"corsDomain=finance.yahoo.com"
        response = requests.get(url, headers=self.HEADERS)
        data = response.json()
        result = data["chart"]["result"][0]
        assert "timestamp" in result
        assert len(result["timestamp"]) == 1
        timestamp = result["timestamp"][0]
        quote = result["indicators"]["quote"][0]
        return BarEvent(datetime.fromtimestamp(timestamp), quote["open"], quote["high"], quote["low"], quote["close"], quote["volume"])


def make_feed(ticker: str, interval: YahooInterval):
    feed = BarFeed()
    feed.history = CsvBarHistory(f"../data/{ticker}.csv", YAHOO_CSV_COLUMNS)
    feed.live_feed = YahooLiveFeed(ticker, interval)
    return feed
