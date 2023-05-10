print("Starting...")

from zipline import run_algorithm
import pandas as pd
import pandas_datareader.data as web

import avg

print("Loaded modules...")

start = pd.Timestamp('2014')
end = pd.Timestamp('2018')

sp500 = web.DataReader('SP500', 'fred', start, end).SP500
benchmark_returns = sp500.pct_change()

print("Running...")

result = run_algorithm(start=start,
                       end=end,
                       initialize=avg.initialize,
                       handle_data=avg.handle_data,
                       analyze=avg.analyze,
                       capital_base=100000,
                       benchmark_returns=benchmark_returns,
                       bundle='quandl',
                       data_frequency='daily')

print("Finished!")
print(result)
