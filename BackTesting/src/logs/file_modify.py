import pandas as pd

df = pd.read_csv("rsi_1h.csv")
df['Open'] = df['Open'] * 1e6
df['Close'] = df['Close'] * 1e6
df['High'] = df['High'] * 1e6
df['Low'] = df['Low'] * 1e6
df['Volume'] = df['Volume'] / 1e6
df.to_csv("rsi_1h.csv", index = False)
