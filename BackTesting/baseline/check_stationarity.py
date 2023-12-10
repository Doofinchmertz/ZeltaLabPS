import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
import talib
from statsmodels.tsa.stattools import adfuller

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("../data/btcusdt_" + timeframe + "_" + name + ".csv")

df = get_data("1h", "total")

diff = df["close"] - df["close"].shift(1)
diff = diff.dropna()
print(len(diff))

adf, p_value, usedlag, nobs, critical_values, icbest = adfuller(diff)
print("p-value: " + str(p_value))