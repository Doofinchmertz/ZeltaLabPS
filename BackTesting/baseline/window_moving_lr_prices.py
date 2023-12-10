import pandas as pd
import sys
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_" + name + ".csv")

time_frame = sys.argv[1]
k = int(sys.argv[2])

df = get_data(time_frame, "total")

X = df.drop(f'Next_{k}_Days_Return', axis=1)
y = df['close'].shift(-1)
X = X[:-1]
y = y[:-1]
df = df[:-1]

model = LinearRegression() 
lookback = int(sys.argv[3])
pred_window = int(sys.argv[4])
for i in range(lookback, len(X) - pred_window, pred_window):
    model.fit(X[i - lookback:i-k], y[i-lookback:i-k])
    y_pred = model.predict(X[i:i+pred_window])
    df.loc[X[i:i+pred_window].index, 'Predicted_Return'] = (y_pred - X[i:i+pred_window]['close'])/X[i:i+pred_window]['close']*1000
df['indicator'] = np.where(df['Predicted_Return'] > 1.5, 1, np.where(df['Predicted_Return'] < -1.5, -1, 0))
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
data.drop(data.index[:lookback], inplace=True)
data.to_csv(f"../src/logs/window_moving_lr_prices.csv")
