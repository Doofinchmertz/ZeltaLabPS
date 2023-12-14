import pandas as pd

df = pd.read_csv('rolling_lr1.csv')
df_signal_1 = df[df['signal'] == -1]
print(df_signal_1['datetime'])
