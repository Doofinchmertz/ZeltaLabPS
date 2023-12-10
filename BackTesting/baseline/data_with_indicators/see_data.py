import pandas as pd

df = pd.read_csv('btcusdt_1h_total.csv')
df = df.tail(int(len(df) * 0.1))
positive_rows = df[df['Next_1_Days_Return'] > 0]
ratio = len(positive_rows) / len(df)
print("Ratio of positive rows:", ratio)
