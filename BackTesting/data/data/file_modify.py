import pandas as pd
from sklearn.model_selection import train_test_split

# Read the CSV file
idx = '3m'
df = pd.read_csv(f'btcusdt_{idx}_total.csv')

# Split the data into train and val sets
train_df, val_df = train_test_split(df, test_size=0.25, shuffle=False)

# Save the train and val sets to separate files
train_df.to_csv(f'btcusdt_{idx}_train.csv', index=False)
val_df.to_csv(f'btcusdt_{idx}_val.csv', index=False)
