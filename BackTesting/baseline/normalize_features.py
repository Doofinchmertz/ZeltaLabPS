from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_" + name + ".csv")

# Tick Size of Data
time_frame = "5m"
# Load data
df_train = get_data(time_frame, 'train')
df_val = get_data(time_frame, 'val')
scaler = StandardScaler()
scaler.fit(df_train.values)
df_train = pd.DataFrame(scaler.transform(df_train.values), index=df_train.index, columns=df_train.columns)
df_val = pd.DataFrame(scaler.transform(df_val.values), index=df_val.index, columns=df_val.columns)

df_train.to_csv("data_with_indicators/btcusdt_" + time_frame + "_train_norm.csv", index=True)
df_val.to_csv("data_with_indicators/btcusdt_" + time_frame + "_val_norm.csv", index=True)
