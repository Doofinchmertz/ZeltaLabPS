import pandas as pd
import numpy as np
import talib
import warnings
import sys
warnings.filterwarnings('ignore')

short_window = int(sys.argv[1])
long_window = int(sys.argv[2])
span_b_window = int (sys.argv[3])
upper_treshold = int(sys.argv[4])
lower_treshold = int(sys.argv[5])
displacement = span_b_window // 2

# short_window = 10
# long_window = 10
# span_b_window = 100
# upper_treshold = 90
# lower_treshold = 10
# displacement = 10 

df = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\data\data\btcusdt_1h_train.csv")

def money_flow_index(data, period=14):
    # Calculate typical price
    typical_price = (data['high'] + data['low'] + data['close']) / 3

    # Calculate raw money flow
    raw_money_flow = typical_price * data['volume']

    # Get the direction of the money flow
    money_flow_direction = [1 if typical_price[i] > typical_price[i - 1] else (-1 if typical_price[i] < typical_price[i - 1] else 0) for i in range(1, len(typical_price))]

    # Pad the money flow direction with 0 for the first element
    money_flow_direction.insert(0, 0)

    # Calculate positive and negative money flow
    positive_money_flow = [0 if direction == -1 else raw_money_flow[i] for i, direction in enumerate(money_flow_direction)]
    negative_money_flow = [0 if direction == 1 else raw_money_flow[i] for i, direction in enumerate(money_flow_direction)]

    # Calculate 14-day sums of positive and negative money flow
    positive_money_flow_sum = pd.Series(positive_money_flow).rolling(window=period, min_periods=1).sum()
    negative_money_flow_sum = pd.Series(negative_money_flow).rolling(window=period, min_periods=1).sum()

    # Calculate money flow index
    money_flow_ratio = positive_money_flow_sum / negative_money_flow_sum
    money_flow_index = 100 - (100 / (1 + money_flow_ratio))

    return money_flow_index

# Example usage
# Assuming you have a DataFrame 'df' with columns 'High', 'Low', 'Close', and 'Volume'
# You can calculate the Money Flow Index like this:
df['MFI'] = money_flow_index(df)

df['flag_1'] = df['MFI'].apply(lambda x: 1 if x > upper_treshold else (-1 if x < lower_treshold else 0))

def generate_signals(df, flag_column):
    compare = 0
    counter = 0

    signals = pd.Series(0, index=df.index, name='signal')

    for i in range(len(df)):
        if df[flag_column].iloc[i] == 1 and compare == 0:
            # No open trade, encounter buy signal
            compare = 1
            signals.iloc[i] = 1

        elif df[flag_column].iloc[i] == -1 and compare == 0:
            # Current buy trade, encounter sell signal or no signal - update stop loss
            signals.iloc[i] = -1
            compare = -1

        elif compare != 0:
            if counter < 10:
                if df[flag_column].iloc[i] == 0:
                    counter += 1
                else:
                    if df[flag_column].iloc[i] == compare:
                        counter = counter // 2
                    else:
                        counter = 0
                        compare = 0
                        signals.iloc[i] = df[flag_column].iloc[i]

            else:
                signals.iloc[i] = -1 * compare
                counter = 0
                compare = 0

    df['signal_1'] = signals

# Example Usage:
# Assuming you have a DataFrame named 'df' with columns 'log' and 'flag'
generate_signals(df, 'flag_1')

# print(df.columns)



## Strategy 2
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

    return data

# Example usage:
# Load your OHLCV data into a DataFrame (replace this with your actual data)


def calculate_obv_flags(data):
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
ohlc_data = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\data\data\btcusdt_1h_train.csv")
# make the index as datetime
ohlc_data.index = pd.to_datetime(ohlc_data['datetime'])
# drop the datetime column as it is now redundant
ohlc_data.drop('datetime', axis=1, inplace=True)
# Calculate Ichimoku Cloud
ohlc_data = calculate_ichimoku_cloud(ohlc_data, short_window=int(short_window), long_window=int(long_window), span_b_window=int(span_b_window), displacement=int(displacement))
# Calculate OBV
ohlc_data = calculate_obv(ohlc_data)
calculate_obv_flags(ohlc_data)
ohlc_data = ohlc_data.dropna()
ohlc_data = ohlc_data.reset_index()
# Select the 5 columns for applying the logic
selected_columns = ['market_direction', 'above_kumo', 'senkou_span_cross', 'kumo_twist', 'tenkan_kijun_cross']

# Define a function to apply the logic
def assign_value(row):
    if row.sum() >= 2:
        return 1
    elif row.sum() <= -2:
        return -1
    else:
        return 0
    
def apply_trading_strategy(df, flag_column, log_column, stop_loss_thresh=-0.07):
    exit_loss = 0
    disable_trading = 0
    compare = 0
    df[log_column] = np.nan

    for i in range(len(df)):
        if df[flag_column].iloc[i] == 1 and compare == 0:
            # No open trade, encounter buy signal
            exit_loss = 0
            buy_price = df["close"].iloc[i]
            compare = 1
            df[log_column].iloc[i] = 1

        elif (df[flag_column].iloc[i] != -1 and compare == 1):
            # Current buy trade, encounter buy signal or no signal - update stop loss
            df[log_column].iloc[i] = 0

            # Calculate pnl, if we exit now
            sell_price = df["close"].iloc[i]
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
            sell_price = df["close"].iloc[i]
            compare = -1
            df[log_column].iloc[i] = -1

        elif (df[flag_column].iloc[i] != 1 and compare == -1):
            # Current sell trade, encounter sell signal or no signal - do nothing, update stop loss
            df[log_column].iloc[i] = 0

            # Calculate pnl, if we exit now
            buy_price = df["close"].iloc[i]
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

    df_filter = df[['datetime', log_column]]
    df_filter.columns = ["datetime", 'signal_2']
    df_filter = df_filter.reset_index(drop=True)
    
    return df_filter

# Example usage:
# Load your DataFrame 'df' with the required columns
# df = ...

# Apply the trading strategy function
ohlc_data['flag'] = ohlc_data[selected_columns].apply(assign_value, axis=1)
result_df = apply_trading_strategy(ohlc_data, flag_column='flag', log_column='signal_2')


df['datetime'] = pd.to_datetime(df['datetime'])
result_df['datetime'] = pd.to_datetime(result_df['datetime'])

# Merge DataFrames on 'datetime' column
df_merged = pd.merge(df, result_df, on='datetime', how='inner')
# print(df_merged.columns)
df_merged['signal'] = np.nan
compare = 0
for i in range(len(df_merged)):

    # Opening a trade
    if df_merged['signal_1'].iloc[i] == 1 and df_merged['signal_2'].iloc[i] == 1 and compare == 0:
        df_merged['signal'].iloc[i] = 1
        compare = 1
    elif df_merged['signal_1'].iloc[i] == -1 and df_merged['signal_2'].iloc[i] == -1 and compare == 0:
        df_merged['signal'].iloc[i] = -1
        compare = -1
    elif df_merged['signal_1'].iloc[i] == 1 and df_merged['signal_2'].iloc[i] == 0 and compare == 0:
        df_merged['signal'].iloc[i] = 1
        compare = 1
    elif df_merged['signal_1'].iloc[i] == -1 and df_merged['signal_2'].iloc[i] == 0 and compare == 0:
        compare = -1
        df_merged['signal'].iloc[i] = -1
    elif df_merged['signal_1'].iloc[i] == 0 and df_merged['signal_2'].iloc[i] == 1 and compare == 0:
        df_merged['signal'].iloc[i] = 1
        compare = 1
    elif df_merged['signal_1'].iloc[i] == 0 and df_merged['signal_2'].iloc[i] == -1 and compare == 0:
        compare = -1
        df_merged['signal'].iloc[i] = -1

    # Closing a trade
    elif df_merged['signal_1'].iloc[i] == -1 and df_merged['signal_2'].iloc[i] == 1 and compare == 1:
        df_merged['signal'].iloc[i] = 0
        compare = 1
    elif df_merged['signal_1'].iloc[i] == 1 and df_merged['signal_2'].iloc[i] == -1 and compare == 1:
        df_merged['signal'].iloc[i] = 0
        compare = 1
    elif df_merged['signal_1'].iloc[i] == -1 and df_merged['signal_2'].iloc[i] == 0 and compare == 1:
        df_merged['signal'].iloc[i] = -1
        compare = 0
    elif df_merged['signal_1'].iloc[i] == 1 and df_merged['signal_2'].iloc[i] == 0 and compare == 1:
        df_merged['signal'].iloc[i] = 0
        compare = 1
    elif df_merged['signal_1'].iloc[i] == 0 and df_merged['signal_2'].iloc[i] == 1 and compare == 1:
        df_merged['signal'].iloc[i] = 0
        compare = 1
    elif df_merged['signal_1'].iloc[i] == 0 and df_merged['signal_2'].iloc[i] == -1 and compare == 1:
        df_merged['signal'].iloc[i] = -1
        compare = 0

    elif df_merged['signal_1'].iloc[i] == -1 and df_merged['signal_2'].iloc[i] == 1 and compare == -1:
        df_merged['signal'].iloc[i] = 0
        compare = -1
    elif df_merged['signal_1'].iloc[i] == 1 and df_merged['signal_2'].iloc[i] == -1 and compare == -1:
        df_merged['signal'].iloc[i] = 0
        compare = -1
    elif df_merged['signal_1'].iloc[i] == -1 and df_merged['signal_2'].iloc[i] == 0 and compare == -1:
        df_merged['signal'].iloc[i] = 0
        compare = -1
    elif df_merged['signal_1'].iloc[i] == 1 and df_merged['signal_2'].iloc[i] == 0 and compare == -1:
        df_merged['signal'].iloc[i] = 1
        compare = 0
    elif df_merged['signal_1'].iloc[i] == 0 and df_merged['signal_2'].iloc[i] == 1 and compare == -1:
        df_merged['signal'].iloc[i] = 1
        compare = 0
    elif df_merged['signal_1'].iloc[i] == 0 and df_merged['signal_2'].iloc[i] == -1 and compare == -1:
        df_merged['signal'].iloc[i] = 0
        compare = -1

    

df_merged['signal'] = df_merged['signal'].fillna(0)
# df_merged['close'] = df_merged['close_x']
# df_merged['open'] = df_merged['open_x']

# Apply the function to create a new column 'final_value'


df_merged.to_csv(rf"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\src\logs\mfi_ichi_{short_window}_{long_window}_{span_b_window}_{upper_treshold}_{lower_treshold}.csv")