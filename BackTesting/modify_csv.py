import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('reversed_file.csv')  # Replace 'your_file.csv' with the actual file name

# Replace the string values in the 'Your_Column' column with float values
df['Close'] = df['Close'].str.replace(',', '').astype(float)
df['Change'] = df['Change'].str.replace(',', '').astype(float)
df['Open'] = df['Open'].str.replace(',', '').astype(float)
df['High'] = df['High'].str.replace(',', '').astype(float)
df['Low'] = df['Low'].str.replace(',', '').astype(float)

# Save the updated DataFrame to a new CSV file
df.to_csv('reversed_file.csv', index=False)