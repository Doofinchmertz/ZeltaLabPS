from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
import matplotlib.pyplot as plt
import talib

df = pd.read_csv("btcusdt_3m_train.csv")
df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=140)

fig, ax1 = plt.subplots()

# Plotting ATR
ax1.plot(df['ATR'], color='blue')
ax1.set_ylabel('ATR', color='blue')

# Creating a second y-axis
ax2 = ax1.twinx()

# Plotting Close
ax2.plot(df['close'], color='red')
ax2.set_ylabel('Close', color='red')

plt.show()
