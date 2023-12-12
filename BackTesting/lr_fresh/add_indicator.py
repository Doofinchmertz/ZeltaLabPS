import pandas as pd
import talib
import numpy as np

name = 'diamond'
ts = '1h'
df = pd.read_csv(f"../data/btcusdt_{ts}_{name}.csv")

df['Next_2h_Return'] = df['close'].shift(-2) / df['close'] - 1
df['Next_2h_Return'] = df['Next_2h_Return']*1000

df['RSI'] = talib.RSI(df['close'], timeperiod=140)
df['RSI'] -= 50
df['RSI'] = df['RSI'].apply(lambda x: x if x > 20 or x < -20 else 0)
df['RSI'] = df['RSI'].apply(lambda x: x - 20 if x >= 20 else x)
df['RSI'] = df['RSI'].apply(lambda x: x + 20 if x <= -20 else x)                            
df.fillna(0,inplace=True)

df['exp_RSI'] = 0
df['exp_RSI'] = np.exp(np.abs(df['RSI']))
df['exp_RSI'] = np.where(df['RSI'] > 0, -df['exp_RSI'], df['exp_RSI'])

df['EMA'] = talib.EMA(df['close'], timeperiod=2)
df['EMA_Slope'] = -df['EMA'].pct_change(1)*100

df['ADOSC'] = talib.ADOSC(df['high'], df['low'], df['close'], df['volume'], fastperiod=2, slowperiod=3)

macd, signal, _ = talib.MACD(df["close"], fastperiod=99, slowperiod=136, signalperiod=47)
df['macd'] = macd
df['signal'] = signal
shifted_signal = df['signal'].shift(1)
shifted_signal.fillna(0, inplace=True)
df['macd'].fillna(0, inplace=True)
df['macd_signal'] = df['signal'] - shifted_signal

df = df.drop(['RSI', 'macd', 'signal', 'EMA'], axis=1)
df.dropna(inplace=True)
df.to_csv(f"data/btcusdt_{ts}_{name}.csv", index=False)