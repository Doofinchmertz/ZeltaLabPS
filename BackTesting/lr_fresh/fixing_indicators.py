import pandas as pd
import matplotlib.pyplot as plt
import talib
import numpy as np
import sys

df = pd.read_csv("../data/btcusdt_1h_train.csv")

df['Next_2h_Return'] = df['close'].shift(-2)/df['close'] - 1
df['Next_2h_Return'] = df['Next_2h_Return']*1000

corr = []
for k in range(2,100):
    df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod = k)
    corr.append(df['ADX'].corr(df['Next_2h_Return']))
plt.plot(range(2,100), corr)
plt.show()