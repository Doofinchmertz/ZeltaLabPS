import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from optimal_constants import *

ts = "1h"  # tick size to trade

## Loading Data
df = pd.read_csv(f"data_with_indicators/btcusdt_{ts}.csv")
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index(df['datetime'], inplace=True)

## Target Variable
y = df['Next_2h_Return']

## Filtering features
X = df.drop(['Next_2h_Return', 'open', 'close', 'datetime', 'volume', 'high', 'low'], axis=1)

## Rolling Linear Regression
look_back = LOOK_BACK_WINDOW  # Training Window
pred_window = PREDICTION_WINDOW  # Prediction Window
k = TARGET_K  # Next k periods return prediction
cut = CUT  # Cut-off for return prediction to generate signal

df['predicted_return'] = 0
model = LinearRegression()
for i in range(look_back, len(X) - pred_window, pred_window):
    # Fitting on training window
    model.fit(X[i - look_back:i - k], y[i - look_back:i - k])
    # Predicting on prediction window
    df.loc[df[i:i + pred_window].index, 'predicted_return'] = model.predict(X[i:i + pred_window])

# Dropping the data before the first prediction
df.drop(df.index[:look_back], inplace=True)

# Generating signals
df['indicator'] = np.where(df['predicted_return'] > cut, 1, np.where(df['predicted_return'] < -cut, -1, 0))
df['signal'] = 0

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
df.to_csv(f"logs/rolling_lr.csv")
