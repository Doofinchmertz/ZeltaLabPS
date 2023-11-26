import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from neuralforecast.core import NeuralForecast
from neuralforecast.models import PatchTST

from neuralforecast.losses.pytorch import MAE
from neuralforecast.losses.numpy import mae, mse
from sklearn.model_selection import train_test_split


def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe):
    return read_file("../../data/btcusdt_" + timeframe + ".csv")

time_frame = "5m"
data = get_data(time_frame)
data['y'] = data['open']
data['ds'] = data.index
data['unique_id'] = data.index
data = data.head(5000)  # Take only the first 100 rows

validation, test = train_test_split(data, test_size=0.5, shuffle=False)
print(data.columns)
print(data.shape, validation.shape, test.shape)

model = [PatchTST(h=96, input_size=192, start_padding_enabled=True)]
nf = NeuralForecast(models=model, freq='5min')

predicted = nf.cross_validation(df = data, val_size=validation.shape[0])
predicted.to_csv("../logs/patch_tst_" + time_frame + ".csv")