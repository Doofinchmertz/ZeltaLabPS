from sklearn.linear_model import LinearRegression, Lasso
import pandas as pd
import sys
import numpy as np

k = sys.argv[2]

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_" + name + ".csv")
