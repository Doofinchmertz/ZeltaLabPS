from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import seaborn as sns
import mplfinance as mpf
import matplotlib.pyplot as plt

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("../data/btcusdt_" + timeframe + "_" + name + ".csv")

time_frame = "30m"

df = get_data(time_frame, 'train')

# Plotting candlesticks
mpf.plot(df.head(100), type='candle', volume=True)

plt.show()


