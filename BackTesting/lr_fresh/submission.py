import pandas as pd
import talib
from sklearn.linear_model import LinearRegression
import numpy as np

ts = '1h'
name = 'diamond'
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

df = pd.read_csv(f"data/btcusdt_1h_{name}.csv")
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index(df['datetime'], inplace=True)

y = df['Next_2h_Return']
X = df.drop(['Next_2h_Return', 'open', 'high', 'low', 'close', 'datetime', 'volume'], axis=1)

look_back = 1248
pred_window = 1056
k = 2
cut = 2.5

df['predicted_return'] = 0
model = LinearRegression()
for i in range(look_back, len(X) - pred_window, pred_window):
    model.fit(X[i-look_back:i-k], y[i-look_back:i-k])
    df.loc[df[i:i+pred_window].index, 'predicted_return'] = model.predict(X[i:i+pred_window])
df['indicator'] = np.where(df['predicted_return'] > cut, 1, np.where(df['predicted_return'] < -cut, -1, 0))
df['signal'] = 0

# Without Stoploss
tot = 0
for index, _ in df.iterrows():
    df.at[index, 'signal'] = 0
    if df.at[index, 'indicator'] == 1:
        if tot == 0 or tot == -1:
            # enter long position/exit short position
            tot += 1
            df.at[index, 'signal'] = 1
    elif df.at[index, 'indicator'] == -1:
        if tot == 0 or tot == 1:
            # enter short position/exit long position
            tot -= 1
            df.at[index, 'signal'] = -1
df.to_csv(f"../src/logs/rolling_lr.csv")