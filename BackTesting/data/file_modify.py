import pandas as pd
from sklearn.model_selection import train_test_split

# Read the CSV file
idx = '1h'
df = pd.read_csv(f'btcusdt_{idx}_gold.csv')
df['datetime'] = pd.to_datetime(df['datetime'])  # Convert datetime column to datetime type
df.set_index(df['datetime'], inplace=True)  # Set datetime column as index
df.drop(columns=['Unnamed: 0'], inplace=True)  # Drop the 'Unnamed: 0' column
# print(df.columns)

df.to_csv(f'btcusdt_{idx}_gold.csv', index=False)



# # Split the data into train and val sets
# train_df, val_df = train_test_split(df, test_size=0.25, shuffle=False)


# # Save the train and val sets to separate files
# train_df.to_csv(f'btcusdt_{idx}_train.csv', index=False)
# val_df.to_csv(f'btcusdt_{idx}_val.csv', index=False)

