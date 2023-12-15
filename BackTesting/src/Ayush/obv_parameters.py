import pandas as pd
import numpy as np
import talib
import warnings
import sys

warnings.filterwarnings('ignore')

short_window = int (sys.argv[1])
long_window = int (sys.argv[2])
span_b_window = int (sys.argv[3])
displacement = int (sys.argv[4])

df = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\data\data\btcusdt_1h_train.csv")

def calculate_ichimoku_cloud(data, short_window=9, long_window=26, span_b_window=52, displacement=26):
    
    data['tenkan_sen'] = (data['high'].rolling(window=short_window).max() + data['low'].rolling(window=short_window).min()) / 2
    data['kijun_sen'] = (data['high'].rolling(window=long_window).max() + data['low'].rolling(window=long_window).min()) / 2
    data['senkou_span_a'] = ((data['tenkan_sen'] + data['kijun_sen']) / 2).shift(displacement)
    data['senkou_span_b'] = ((data['high'].rolling(window=span_b_window).max() + data['low'].rolling(window=span_b_window).min()) / 2).shift(displacement)
    # Tenkan Sen and Kijun Sen Cross signals
    data['tenkan_kijun_cross'] = 0
    data.loc[data['tenkan_sen'] > data['kijun_sen'], 'tenkan_kijun_cross'] = 1
    data.loc[data['tenkan_sen'] < data['kijun_sen'], 'tenkan_kijun_cross'] = -1
    # Kumo Signals
    data['above_kumo'] = 0
    data.loc[data['close'] > data[['senkou_span_a', 'senkou_span_b']].max(axis=1), 'above_kumo'] = 1
    data.loc[data['close'] < data[['senkou_span_a', 'senkou_span_b']].min(axis=1), 'above_kumo'] = -1
    # Senkou Span Cross signals
    data['senkou_span_cross'] = 0
    data.loc[data['senkou_span_a'] > data['senkou_span_b'], 'senkou_span_cross'] = 1
    data.loc[data['senkou_span_a'] < data['senkou_span_b'], 'senkou_span_cross'] = -1
    # Kumo Twist signals
    data['kumo_twist'] = 0
    data.loc[(data['senkou_span_a'].shift(1) > data['senkou_span_b'].shift(1)) & (data['senkou_span_a'] <= data['senkou_span_b']), 'kumo_twist'] = 1
    data.loc[(data['senkou_span_a'].shift(1) < data['senkou_span_b'].shift(1)) & (data['senkou_span_a'] >= data['senkou_span_b']), 'kumo_twist'] = -1
    return data

def calculate_obv(data):
    data['daily_return'] = data['close'].pct_change()
    data['obv'] = (data['daily_return'].fillna(0).apply(lambda x: 1 if x > 0 else -1) * data['volume']).cumsum()
    # Bullish and bearish signals based on OBV
    data['bullish_signal'] = (data['obv'] > data['obv'].shift(1)).astype(int)
    data['bearish_signal'] = (data['obv'] < data['obv'].shift(1)).astype(int)
    # Bullish and bearish divergence signals
    data['bullish_divergence'] = ((data['close'] < data['close'].shift(1)) & (data['obv'] > data['obv'].shift(1))).astype(int)
    data['bearish_divergence'] = ((data['close'] > data['close'].shift(1)) & (data['obv'] < data['obv'].shift(1))).astype(int)
    # Bullish and bearish confirmation signals
    data['bullish_confirmation'] = ((data['close'] > data['close'].shift(1)) & (data['obv'] > data['obv'].shift(1))).astype(int)
    data['bearish_confirmation'] = ((data['close'] < data['close'].shift(1)) & (data['obv'] < data['obv'].shift(1))).astype(int)
    # Create an overall flag column
    data['market_direction'] = 0  # 0 indicates no clear direction
    data.loc[data['bearish_confirmation'] == 1, 'market_direction'] = -1
    data.loc[data['bullish_confirmation'] == 1, 'market_direction'] = 1
    return data

# Example usage:
# Load your OHLCV data into a DataFrame (replace this with your actual data)
ohlc_data = df.copy()
# make the index as datetime
ohlc_data.index = pd.to_datetime(ohlc_data['datetime'])
# drop the datetime column as it is now redundant
ohlc_data.drop('datetime', axis=1, inplace=True)
# Calculate Ichimoku Cloud
ohlc_data = calculate_ichimoku_cloud(ohlc_data, short_window=int(short_window), long_window=int(long_window), span_b_window=int(span_b_window), displacement=int(displacement))
# Calculate OBV
ohlc_data = calculate_obv(ohlc_data)


ohlc_data = ohlc_data.dropna()
ohlc_data = ohlc_data.reset_index()

selected_columns = ['market_direction', 'above_kumo', 'senkou_span_cross', 'kumo_twist', 'tenkan_kijun_cross']

# Define a function to apply the logic
def assign_value(row):
    if row.sum() >= 2:
        return 1
    elif row.sum() <= -2:
        return -1
    else:
        return 0

# Apply the function to create a new column 'final_value'
ohlc_data['flag'] = ohlc_data[selected_columns].apply(assign_value, axis=1)

def apply_trading_strategy(df, flag_column, log_column, stop_loss_thresh=-0.07):
    exit_loss = 0
    disable_trading = 0
    compare = 0
    df[log_column] = np.nan

    for i in range(len(df)):
        if df[flag_column].iloc[i] == 1 and compare == 0:
            # No open trade, encounter buy signal
            exit_loss = 0
            buy_price = df["open"].iloc[i]
            compare = 1
            df[log_column].iloc[i] = 1

        elif (df[flag_column].iloc[i] != -1 and compare == 1):
            # Current buy trade, encounter buy signal or no signal - update stop loss
            df[log_column].iloc[i] = 0
            # Calculate pnl, if we exit now
            sell_price = df["open"].iloc[i]
            exit_loss = (sell_price - buy_price) / buy_price
            # Exit trade, if the loss is higher than stop loss
            if exit_loss < stop_loss_thresh and disable_trading == 0:
                df[log_column].iloc[i] = -1
                disable_trading = 1

        elif df[flag_column].iloc[i] == -1 and compare == 1:
            # Current buy trade, encounter sell signal
            # Exit trade
            df[log_column].iloc[i] = -1
            compare = 0
            exit_loss = 0
            # If trade was already exited before, check for disable trading flag here, do nothing here
            if disable_trading == 1:
                disable_trading = 0
                df[log_column].iloc[i] = 0

        # SHORT TRADES
        elif df[flag_column].iloc[i] == -1 and compare == 0:
            # No open trade, encounter sell signal
            exit_loss = 0
            sell_price = df["open"].iloc[i]
            compare = -1
            df[log_column].iloc[i] = -1

        elif (df[flag_column].iloc[i] != 1 and compare == -1):
            # Current sell trade, encounter sell signal or no signal - do nothing, update stop loss
            df[log_column].iloc[i] = 0
            # Calculate pnl, if we exit now
            buy_price = df["open"].iloc[i]
            exit_loss = (sell_price - buy_price) / sell_price
            # Exit trade, if the loss is higher than stop loss
            if exit_loss < stop_loss_thresh and disable_trading == 0:
                df[log_column].iloc[i] = 1
                disable_trading = 1

        elif df[flag_column].iloc[i] == 1 and compare == -1:
            # Exit trade
            df[log_column].iloc[i] = 1
            compare = 0
            exit_loss = 0
            # If trade was already exited before, check for disable trading flag here, do nothing here
            if disable_trading == 1:
                disable_trading = 0
                df[log_column].iloc[i] = 0

        elif df[flag_column].iloc[i] == 0 and compare == 0:
            df[log_column].iloc[i] == 0
    # Fill in any missing values in the new column with 0.
    df[log_column].fillna(0, inplace=True)

    # Close out positions (if needed)
    df[log_column].iloc[-1] = -np.sum(df[log_column])

    # df_filter = df[['datetime', 'open', 'high', 'low', 'close', 'volume', log_column]]
    # df_filter.columns = ["datetime", 'open', 'high', 'low', 'close', 'volume', 'signal']
    # df_filter = df_filter.reset_index(drop=True)
    
    return df

# Example usage:
# Load your DataFrame 'df' with the required columns
# df = ...

# Apply the trading strategy function
result_df = apply_trading_strategy(ohlc_data, flag_column='flag', log_column='signal')
result_df.to_csv(rf"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\src\logs\obv_{short_window}_{long_window}_{span_b_window}_{displacement}.csv")

