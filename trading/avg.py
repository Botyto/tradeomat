import pandas
from zipline.api import order_target, record, symbol

import tinfo

class ContextTInfo(tinfo.TradingAlgorithm):
    i: int
    asset: tinfo.Asset


from zipline.api import order_target, record, symbol
import matplotlib.pyplot as plt

STOCK = "GOOG"  # "AAPL"

def initialize(context: ContextTInfo):
    print("at date 0")
    context.i = 0
    context.asset = symbol(STOCK)

SHORT = 50
LONG = 200

def handle_data(context: ContextTInfo, data: tinfo.BarData):
    # Skip first 300 days to get full windows
    print("\rat date", context.i)
    context.i += 1
    if context.i < LONG:
        return

    # Compute averages
    # data.history() has to be called with the same params
    # from above and returns a pandas dataframe.
    short_mavg = data.history(context.asset, 'price', bar_count=SHORT, frequency="1d").mean()
    long_mavg = data.history(context.asset, 'price', bar_count=LONG, frequency="1d").mean()

    # Trading logic
    if short_mavg > long_mavg:
        # order_target orders as many shares as needed to
        # achieve the desired number of shares.
        context.order_target(context.asset, 100)
    elif short_mavg < long_mavg:
        context.order_target(context.asset, 0)

    # Save values for later inspection
    recorded_data = {
        context.asset.symbol: data.current(context.asset, 'price'),
        "short_mavg": short_mavg,
        "long_mavg": long_mavg,
    }
    record(**recorded_data)

def analyze(context: ContextTInfo, perf: pandas.DataFrame):
    print()
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    perf.portfolio_value[LONG:].plot(ax=ax1)
    ax1.set_ylabel('portfolio value in $')
    ax2 = fig.add_subplot(212)
    perf[STOCK].plot(ax=ax2)
    perf[['short_mavg', 'long_mavg']].plot(ax=ax2)
    perf_trans = perf.loc[[t != [] for t in perf.transactions]]
    buys = perf_trans.loc[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
    sells = perf_trans.loc[[t[0]['amount'] < 0 for t in perf_trans.transactions]]
    ax2.plot(buys.index, perf.short_mavg.loc[buys.index], '^', markersize=10, color='m')
    ax2.plot(sells.index, perf.short_mavg.loc[sells.index], 'v', markersize=10, color='k')
    ax2.set_ylabel('price in $')
    plt.legend(loc=0)
    # plt.show()
    plt.waitforbuttonpress()
