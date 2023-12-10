import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
import talib
from sklearn.preprocessing import StandardScaler

def calculate_rsi(data, window=14):
    # Calculate daily price changes
    delta = data['close'].diff(1)

    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    # Calculate average gains and losses over the specified window
    avg_gains = gains.rolling(window=window, min_periods=1).mean()
    avg_losses = losses.rolling(window=window, min_periods=1).mean()

    # Calculate relative strength (RS)
    rs = avg_gains / avg_losses

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi


k = sys.argv[2]
k = int(k)

time_frame = sys.argv[1]

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("../data/btcusdt_" + timeframe + "_" + name + ".csv")


for name in ["train", "total", "val"]:
    # Load data
    df = get_data(time_frame, name)
    df.head()

    # Indicators
    df['Daily_Return'] = df['close'].pct_change()*1000

    # Next k Days Return (Cumulative)

    df[f'Next_{k}_Days_Return'] = df['close'].pct_change(k).shift(-k)*1000


    # Adding exp_RSI
    df['RSI'] = talib.RSI(df['close'], timeperiod=140)
    df['RSI'] -= 50
    df['RSI'] = df['RSI'].apply(lambda x: x if x > 20 or x < -20 else 0)
    df['RSI'] = df['RSI'].apply(lambda x: x - 20 if x >= 20 else x)
    df['RSI'] = df['RSI'].apply(lambda x: x + 20 if x <= -20 else x)                            
    df.fillna(0,inplace=True)

    df['exp_RSI'] = 0
    df['exp_RSI'] = np.exp(np.abs(df['RSI']))
    df['exp_RSI'] = np.where(df['RSI'] > 0, -df['exp_RSI'], df['exp_RSI'])

    # Scale exp_RSI
    scaler = StandardScaler()
    df['exp_RSI'] = scaler.fit_transform(df['exp_RSI'].values.reshape(-1,1))



    # Adding EMA slope
    df['EMA'] = talib.EMA(df['close'], timeperiod=2)


    # FIND SLOPE OF EMA
    df['EMA_Slope'] = -df['EMA'].pct_change(1)*100
    df1 = df[(df['EMA_Slope'] > 0)]
    df.fillna(0, inplace=True)

    # Scale Slope
    scaler = StandardScaler()
    df['EMA_Slope'] = scaler.fit_transform(df['EMA_Slope'].values.reshape(-1, 1))


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

    df['macd_signal'] = df['signal'] - shifted_signal

    # Drop columns macd, signal, EMA, high, low
    df = df.drop(['macd', 'signal', 'EMA', 'high', 'low'], axis=1)

    # Drop rows with any Nan value
    df = df.dropna()

    # Get the final df with indicators to junk.csv
    df.to_csv("data_with_indicators/btcusdt_" + time_frame + "_" + name + ".csv")