import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
import talib

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("../data/btcusdt_" + timeframe + "_" + name + ".csv")

df = get_data("1h", "train")

df['CCI'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=10)
df['Slow_EMA'] = talib.EMA(df['close'], timeperiod=30)
df['Fast_EMA'] = talib.EMA(df['close'], timeperiod=10)

df['indicator'] = 0
df['indicator'] = np.where(((df['CCI'] > 100) & (df['CCI'] < 110)) | df['CCI'] < -110, 1, np.where(((df['CCI'] < -100) & (df['CCI'] > -110)) | df['CCI'] > 110, -1, 0))

data = df
tot = 0
for index, _ in data.iterrows():
    data.at[index, 'signal'] = 0
    if data.at[index, 'indicator'] == 1:
        if tot == 0 or tot == -1:
            # enter long position/exit short position
            tot += 1
            data.at[index, 'signal'] = 1
    elif data.at[index, 'indicator'] == -1:
        if tot == 0 or tot == 1:
            # enter short position/exit long position
            tot -= 1
            data.at[index, 'signal'] = -1
    else:
        if tot == 1:
            # exit long position
            data.at[index, 'signal'] = -1
        elif tot == -1:
            # exit short position
            data.at[index, 'signal'] = 1
        tot = 0
data.to_csv("../src/logs/check_cci.csv")