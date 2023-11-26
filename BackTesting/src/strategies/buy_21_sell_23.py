import pandas as pd
import datetime

def read_file(filename):
    return pd.read_csv(filename, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe):
    return read_file("../../data/btcusdt_" + timeframe + ".csv")


def buy_21_sell_23(data):
    for index, row in data.iterrows():
        timestamp = data.at[index, 'datetime']
        data.at[index, 'signal'] = 0
        if '21:30:00' in timestamp:
            data.at[index, 'signal'] = 1
        if '22:30:00' in timestamp:
            data.at[index, 'signal'] = -1
        if '02:30:00' in timestamp:
            data.at[index, 'signal'] = -1
        if '04:30:00' in timestamp:
            data.at[index, 'signal'] = 1
    return data

time_frame = "1h"
# Load data
data = get_data(time_frame)

# Apply EMA crossover strategy
data = buy_21_sell_23(data)

# Save to CSV
data.to_csv("../logs/buy_21_sell_23_" + time_frame + ".csv")