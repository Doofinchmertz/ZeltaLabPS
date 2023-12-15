import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
import talib
from sklearn.preprocessing import StandardScaler
from Utils import *


k = 2
k = int(k)

time_frame = "1h"

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("../data/btcusdt_" + timeframe + "_" + name + ".csv")


# Load data
df = get_data(time_frame, "complete")

# # Take first 60% of df and store it in df
# df = df.head(int(0.8 * len(df)))

# Indicators
df['Daily_Return'] = df['close'].pct_change()*1000

# Next k Days Return (Cumulative)

df[f'Next_{k}_Days_Return'] = df['close'].pct_change(k).shift(-k)*1000


# Adding exp_RSI
df['RSI'] = talib.RSI(df['close'], timeperiod=80)
# df['RSI'] = calculate_rsi(df, window=140)
df['RSI'] -= 50
df['RSI'] = df['RSI'].apply(lambda x: x if x > 20 or x < -20 else 0)
df['RSI'] = df['RSI'].apply(lambda x: x - 20 if x >= 20 else x)
df['RSI'] = df['RSI'].apply(lambda x: x + 20 if x <= -20 else x)                            
df.fillna(0,inplace=True)

df['exp_RSI'] = 0
df['exp_RSI'] = np.exp(np.abs(df['RSI']))
df['exp_RSI'] = np.where(df['RSI'] > 0, -df['exp_RSI'], df['exp_RSI'])

# Scale exp_RSI
scaler1 = StandardScaler()
df['exp_RSI'] = scaler1.fit_transform(df['exp_RSI'].values.reshape(-1,1))


# print(money_flow_index(df,14).columns)
df['MFI'] = list(money_flow_index(df, 14))

# Adding EMA slope
df['EMA'] = talib.EMA(df['close'], timeperiod=2)


# FIND SLOPE OF EMA
df['EMA_Slope'] = -df['EMA'].pct_change(1)*100
df1 = df[(df['EMA_Slope'] > 0)]
df.fillna(0, inplace=True)

# Scale Slope
scaler2 = StandardScaler()
df['EMA_Slope'] = scaler2.fit_transform(df['EMA_Slope'].values.reshape(-1, 1))


# Adding change in MACD
fast = 12
slow = 26
signal = 18
macd, signal, _ = talib.MACD(df["close"], fastperiod=fast, slowperiod=slow, signalperiod=signal)
df['macd'] = macd
df['signal'] = signal

shifted_signal = df['signal'].shift(1)
shifted_signal.fillna(0, inplace=True)
df['macd'].fillna(0, inplace=True)

# df['macd_signal'] = df['signal'] - shifted_signal

# Drop columns macd, signal, EMA, high, low
df = df.drop(['macd', 'signal', 'EMA', 'high', 'low'], axis=1)

# Drop rows with any Nan value
df = df.dropna()

# Get the final df with indicators to junk.csv
df.to_csv("data_with_new_indicators/btcusdt_" + time_frame + "_" + "train" + ".csv")



df = get_data(time_frame, "sahi")

df = df[df['volume']!=0]


# Indicators
df['Daily_Return'] = df['close'].pct_change()*1000

# Next k Days Return (Cumulative)

df[f'Next_{k}_Days_Return'] = df['close'].pct_change(k).shift(-k)*1000


# Adding exp_RSI
df['RSI'] = talib.RSI(df['close'], timeperiod=80)
# df['RSI'] = calculate_rsi(df, window=140)
df['RSI'] -= 50
df['RSI'] = df['RSI'].apply(lambda x: x if x > 20 or x < -20 else 0)
df['RSI'] = df['RSI'].apply(lambda x: x - 20 if x >= 20 else x)
df['RSI'] = df['RSI'].apply(lambda x: x + 20 if x <= -20 else x)                            
df.fillna(0,inplace=True)

df['exp_RSI'] = 0
df['exp_RSI'] = np.exp(np.abs(df['RSI']))
df['exp_RSI'] = np.where(df['RSI'] > 0, -df['exp_RSI'], df['exp_RSI'])

# Scale exp_RSI
df['exp_RSI'] = scaler1.transform(df['exp_RSI'].values.reshape(-1,1))

df['MFI'] = list(money_flow_index(df, 14))

# Adding EMA slope
df['EMA'] = talib.EMA(df['close'], timeperiod=2)


# FIND SLOPE OF EMA
df['EMA_Slope'] = -df['EMA'].pct_change(1)*100
df1 = df[(df['EMA_Slope'] > 0)]
df.fillna(0, inplace=True)

# Scale Slope
df['EMA_Slope'] = scaler2.transform(df['EMA_Slope'].values.reshape(-1, 1))


# Adding change in MACD
fast = 12
slow = 26
signal = 18
macd, signal, _ = talib.MACD(df["close"], fastperiod=fast, slowperiod=slow, signalperiod=signal)
df['macd'] = macd
df['signal'] = signal

shifted_signal = df['signal'].shift(1)
shifted_signal.fillna(0, inplace=True)
df['macd'].fillna(0, inplace=True)

# df['macd_signal'] = df['signal'] - shifted_signal

# Drop columns macd, signal, EMA, high, low
df = df.drop(['macd', 'signal', 'EMA', 'high', 'low'], axis=1)

# Drop rows with any Nan value
df = df.dropna()

# Get the final df with indicators to junk.csv
df.to_csv("data_with_new_indicators/btcusdt_" + time_frame + "_" + "val" + ".csv")