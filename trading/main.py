class SymbolSentiment:
    symbol: str
    sentiment: float

    def __init__(self, symbol: str, sentiment: float):
        self.symbol = symbol
        self.sentiment = sentiment

import twitter
import backtrader as bt
from backtrader.utils.py3 import with_metaclass
class TwitterData(with_metaclass(bt.feed.MetaAbstractDataBase, SymbolSentiment)):
    _scraper: twitter.TwitterScraper

    def start(self):
        self._scraper = twitter.TwitterScraper(warmup=True)

    def _load(self):
        tweets = self._scraper.get_tweets("elonmusk")
        pass


import datetime
class TestStrategy(bt.Strategy):
    params = {"maperiod": 15, "idx": 0}

    def log(self, txt, dt=None):
        return
        dt = dt or self.datas[self.p.idx].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[self.p.idx].close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[self.p.idx], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        if self.order:
            return
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy, idx=0)
    start = datetime.datetime(2018, 1, 1)
    end = datetime.datetime(2018, 12, 31)

    data1 = bt.feeds.YahooFinanceCSVData(
        dataname="AAPL.csv",
        fromdate=start,
        todate=end,
        reverse=False)
    cerebro.adddata(data1)
    data2 = bt.feeds.YahooFinanceCSVData(
        dataname="EURUSD=X.csv",
        fromdate=start,
        todate=end,
        reverse=False)
    cerebro.adddata(data2)

    cerebro.broker.setcash(1000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.01)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.plot()
