import pandas as pd

df = pd.read_csv('mfi.csv')
df.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1, inplace=True)
df.to_csv('mfi.csv', index=False)