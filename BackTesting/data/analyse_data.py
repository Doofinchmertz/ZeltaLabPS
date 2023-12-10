from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("btcusdt_1h_total.csv")
decomposition = seasonal_decompose(x=df['close'], model='additive', period = 12) 
decomposition.plot()
plt.show()