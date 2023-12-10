import pandas as pd
import numpy as np
import sys
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_" + name + ".csv")

df_train = get_data("30m", "train")
df_val = get_data("30m", "val")

y_train = pd.DataFrame(df_train['close'])
y_val = pd.DataFrame(df_val['close'])
y_train.index = pd.to_datetime(y_train.index, format='%Y-%m-%d')
y_val.index = pd.to_datetime(df_val.index, format="%Y-%m-%d")

ARIMA_model = SARIMAX(y_train, order=(1, 0, 1))
ARIMA_model = ARIMA_model.fit()

y_pred_val = ARIMA_model.get_forecast(len(df_val.index))
y_pred_val_df = y_pred_val.conf_int(alpha=0.05)
y_pred_val_df["Predictions"] = ARIMA_model.predict(start = y_pred_val_df.index[0], end = y_pred_val_df.index[-1])
y_pred_val_df.index = df_val.index
y_pred_out = y_pred_val_df["Predictions"]

