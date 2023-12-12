import pandas as pd

df = pd.read_csv("../data/btcusdt_1h_train.csv")

median_window = 10
thresh = 4

for i in range(median_window, len(df)):
    median = df['close'][i-median_window:i].median()
    if df['close'][i] < median*(1 - thresh/100):
        df.at[i, 'indicator'] = 1
    elif df['close'][i] > median*(1 + thresh/100):
        df.at[i, 'indicator'] = -1
    else:
        df.at[i, 'indicator'] = 0

df['signal'] = 0
tot = 0
for index, _ in df.iterrows():
    df.at[index, 'signal'] = 0
    if df.at[index, 'indicator'] == 1:
        if tot == 0 or tot == -1:
            # enter long position/exit short position
            tot += 1
            df.at[index, 'signal'] = 1
    elif df.at[index, 'indicator'] == -1:
        if tot == 0 or tot == 1:
            # enter short position/exit long position
            tot -= 1
            df.at[index, 'signal'] = -1

df.to_csv("../src/logs/median_reversion.csv")