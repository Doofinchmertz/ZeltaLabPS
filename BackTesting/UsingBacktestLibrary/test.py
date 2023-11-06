import yfinance as yf
import pandas as pd

def get_data(ticker:str='AAPL',from_date:str='2020-01-01',to_date:str='2022-11-30',interval:str='1d') -> pd.DataFrame:
    yf_ticker = yf.Ticker(ticker)
    return yf_ticker.history(start=from_date,end=to_date,interval=interval)

import backtesting as bt
from backtesting import Strategy, Backtest
from backtesting.lib import crossover
import pandas as pd

def MovingAverage(closes:pd.Series, n:int) -> pd.Series:
    return pd.Series(closes).rolling(n).mean()

class SmaCross(Strategy):
    sma_fast = 12
    sma_slow = 24
    
    def init(self):
        self.sma1 = self.I(MovingAverage, self.data.Close, self.sma_fast)
        self.sma2 = self.I(MovingAverage, self.data.Close, self.sma_slow)

    def next(self):
        if not self.position and crossover(self.sma1, self.sma2):
            self.buy()
        elif self.position and crossover(self.sma2, self.sma1):
            self.position.close()

data = get_data(ticker='AAPL',from_date='2020-01-01',to_date='2022-11-30')
bt = Backtest(data, SmaCross, cash=10_000, commission=0,exclusive_orders=True)
stats = bt.run()
print(stats)
print(stats._trades)
bt.plot()