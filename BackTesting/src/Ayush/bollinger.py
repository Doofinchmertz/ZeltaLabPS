import pandas as pd
import numpy as np
import sys
import warnings
warnings.filterwarnings('ignore')


#optimum parameter
length=int(sys.argv[1])
mult=float(sys.argv[2])

df1 = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\dataset\train\btcusdt_1h_train.csv")
df2 = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\dataset\test\btcusdt_1h_test.csv")

df = pd.concat([df1, df2], ignore_index=True)
df = df.reset_index(drop=True)


def calculate_bollinger_bands(df, length, mult):
    """Calculate Bollinger Bands."""
    basis = df['close'].rolling(window=length).mean()
    dev = df['close'].rolling(window=length).std()
    df['upper_threshold'] = basis + (mult * dev)
    df['lower_threshold'] = basis - (mult * dev)
    return df

def determine_indicator(df):
    """Determine the market situation for trading."""
    df['indicator'] = 0
    df.loc[df['close'] > df['upper_threshold'], 'indicator'] = 1
    df.loc[df['close'] < df['lower_threshold'], 'indicator'] = -1
    return df

def apply_trading_strategy(df, flag_column, log_column, stop_loss_thresh=-0.07):
    """Apply trading strategy based on Bollinger Bands."""
    exit_loss = 0
    compare = 0
    df[log_column] = np.nan

    for i in range(len(df)):
        if df[flag_column].iloc[i] == 1 and compare == 0:
            exit_loss = 0
            buy_price = df["close"].iloc[i]
            compare = 1
            df[log_column].iloc[i] = 1
        elif (df[flag_column].iloc[i] != -1 and compare == 1):
            df[log_column].iloc[i] = 0
            sell_price = df["close"].iloc[i]
            exit_loss = (sell_price - buy_price) / buy_price
            if exit_loss < stop_loss_thresh:
                df[log_column].iloc[i] = -1
                compare = 0
        elif df[flag_column].iloc[i] == -1 and compare == 1:
            df[log_column].iloc[i] = -1
            compare = 0
        elif df[flag_column].iloc[i] == -1 and compare == 0:
            exit_loss = 0
            sell_price = df["close"].iloc[i]
            compare = -1
            df[log_column].iloc[i] = -1
        elif (df[flag_column].iloc[i] != 1 and compare == -1):
            df[log_column].iloc[i] = 0
            buy_price = df["close"].iloc[i]
            exit_loss = (sell_price - buy_price) / sell_price
            if exit_loss < stop_loss_thresh:
                df[log_column].iloc[i] = 1
                compare = 0
        elif df[flag_column].iloc[i] == 1 and compare == -1:
            df[log_column].iloc[i] = 1
            compare = 0
        elif df[flag_column].iloc[i] == 0 and compare == 0:
            df[log_column].iloc[i] = 0

    df[log_column].fillna(0, inplace=True)
    df[log_column].iloc[-1] = -np.sum(df[log_column])
    return df

# Calculate Bollinger Bands
df = calculate_bollinger_bands(df, length, mult)

# Determine Indicator
df = determine_indicator(df)

# Apply Trading Strategy
df = apply_trading_strategy(df, flag_column='indicator', log_column='signal')

# Save to CSV
df.to_csv(rf"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\src\logs\ollin_{length}_{mult}.csv")