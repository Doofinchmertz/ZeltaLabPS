import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys

name = sys.argv[1] if len(sys.argv) > 1 else "train" # "train", "test", "val"

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe, name):
    return read_file("data_with_indicators/btcusdt_" + timeframe + "_" + name + ".csv")

# Tick Size of Data
time_frame = "1h"
# Load data
df = get_data(time_frame, name)
df.head()

# Calculate the correlation matrix
correlation_matrix = df.corr()

# Plot the correlation heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()

