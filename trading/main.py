import asyncio

import engine.engine
import engine.data
import engine.barfeed

feed = engine.barfeed.BarFeed()
feed.history = engine.barfeed.CsvBarHistory("../binance_btcusdt_day.csv")

data = engine.data.EventAggregator()
data.feeds.append(feed)

eng = engine.engine.Engine()
eng.aggregator = data
task = eng.start()
asyncio.get_event_loop().run_until_complete(task)
