import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_total.csv")

time_frame = "5m"

df = get_data(time_frame)

df['indicator'] = 0
df['indicator'] = np.where(0.9985*df['close'] > df['close'].shift(-25), -11, np.where(1.0015*df['close'] < df['close'].shift(-25), 1, 0))

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
    else:
        if tot == 1:
            # exit long position
            data.at[index, 'signal'] = -1
        elif tot == -1:
            # exit short position
            data.at[index, 'signal'] = 1
        tot = 0
data.to_csv("../src/logs/check_25_" + time_frame + ".csv")