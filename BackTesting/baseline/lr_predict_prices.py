import pandas as pd
import numpy as np
import sys
from sklearn.linear_model import LinearRegression

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_" + name + ".csv")

df_train = get_data("30m", "train")
df_val = get_data("30m", "val")

X_train = df_train.drop(['Next_1_Days_Return'], axis=1)
y_train = df_train['close'].shift(-1)
X_val = df_val.drop(['Next_1_Days_Return'], axis=1)
y_val = df_val['close'].shift(-1)
X_train = X_train[:-1]
y_train = y_train[:-1]
X_val = X_val[:-1]
y_val = y_val[:-1]
df_train = df_train[:-1]
df_val = df_val[:-1]

model = LinearRegression()
model.fit(X_train, y_train)

y_pred_train = model.predict(X_train)
y_pred_val = model.predict(X_val)

y_pred_train_return = (y_pred_train / X_train['close'] - 1)*1000
y_pred_val_return = (y_pred_val / X_val['close'] - 1)*1000

df_train['indicator'] = np.where(y_pred_train_return > 1, 1, np.where(y_pred_train_return < -1, -1, 0))
df_val['indicator'] = np.where(y_pred_val_return > 1, 1, np.where(y_pred_val_return < -1, -1, 0))

data = df_train
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
data.to_csv(f"../src/logs/lr_prices_train.csv")

data = df_val
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
data.to_csv(f"../src/logs/lr_prices_val.csv")


