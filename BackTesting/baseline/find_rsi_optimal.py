import multiprocessing
from sklearn.linear_model import LinearRegression, Lasso
import pandas as pd
import sys
import numpy as np
import talib


def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("../data/btcusdt_" + timeframe + "_" + name + ".csv")

k = int(sys.argv[2])
window = int(sys.argv[1])
time_frame = sys.argv[3]

df = get_data(time_frame, "total")

# RSI using TA-Lib
df['RSI'] = talib.RSI(df['close'], window)

# Make indicator +1, -1, 0 using RSI
df['indicator'] = 0
df['indicator'] = np.where(df['RSI'] > 70, -1, np.where(df['RSI'] < 30, 1, 0))

# Define the dependent variable using Next k Days Return
df[f'Next_{k}_Days_Return'] = df['close'].pct_change(k).shift(-k)*1000

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

data.to_csv(f"logs/rsi_total_{window}_{k}_{time_frame}.csv")