import matplotlib
import pandas as pd
import numpy as np
import sys


def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)


def get_data(timeframe, name):
    return read_file("data_with_new_indicators/btcusdt_" + timeframe + "_" + name + ".csv")


