import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys


name = sys.argv[1] # "train", "test", "val"

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("../data/btcusdt_" + timeframe + "_" + name + ".csv")

# Tick Size of Data
time_frame = "5m"
# Load data
df = get_data(time_frame, name)
df.head()

# Indicators
df['Daily_Return'] = df['close'].pct_change()*1000

# Next k Days Return (Cumulative)
k = 1
df[f'Next_{k}_Days_Return'] = df['close'].pct_change(k).shift(-k)*1000

# RSI
window = 14
delta = df['close'].diff(1)
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=window).mean()
avg_loss = loss.rolling(window=window).mean()
rs = avg_gain / avg_loss
df['RSI'] = 100 - (100 / (1 + rs))

# MACD
short_window = 12
long_window = 26
signal_window = 9
df['Short_MA'] = df['close'].rolling(window=short_window).mean()
df['Long_MA'] = df['close'].rolling(window=long_window).mean()
df['MACD'] = df['Short_MA'] - df['Long_MA']
df['Signal_Line'] = df['MACD'].rolling(window=signal_window).mean()

# ROC (Previous n day return)
n = 5
df['ROC'] = df['close'].pct_change(n) * 100

# OBV
df['OBV'] = np.where(df['close'] > df['close'].shift(1), df['volume'], -df['volume'])
df['OBV'] = df['OBV'].cumsum()

# O-C
df['o_c'] = df['open'] - df['close']

# (O-C)*V
df['o_c*v'] = df['o_c']*df['volume']

# H-L
df['h_l'] = df['high'] - df['low']

# Now df has open, close, volume, Daily Return, Next_k_Days_Return, RSI, Signal_Line, ROC, OBV
df = df.drop(['high', 'low', 'MACD', 'Short_MA', 'Long_MA'], axis=1)

# Drop rows with any Nan value
df = df.dropna()

# Get the final df with indicators to junk.csv
df.to_csv("data_with_indicators/btcusdt_" + time_frame + "_" + name + ".csv")