import pandas as pd

def read_file(filename):
    return pd.read_csv(filename, index_col=0, parse_dates=True, infer_datetime_format=True)

def get_data(timeframe):
    return read_file("../../data/btcusdt_" + timeframe + ".csv")


def calculate_ema(data, window, column='close'):
    return data[column].ewm(span=window, adjust=False).mean()

def ema_crossover(data, short_window=12, long_window=26):
    data['short_ema'] = calculate_ema(data, short_window)
    data['long_ema'] = calculate_ema(data, long_window)
    data['indicator'] = 0

    # Buy signal
    data.loc[data['short_ema'] > data['long_ema'], 'indicator'] = 1

    # Sell signal
    data.loc[data['short_ema'] < data['long_ema'], 'indicator'] = -1
    
    tot = 0
    for index, _ in data.iterrows():
        data.at[index, 'signal'] = 0
        if data.at[index, 'indicator'] == 1:
            if tot == 0 or tot == -1:
                # enter long position/exit short position
                tot += 1
                data.at[index, 'signal'] = 1
        elif data.at[index, 'indicator'] == -1:
            if tot == 0 or tot == 1:
                # enter short position/exit long position
                tot -= 1
                data.at[index, 'signal'] = -1
        else:
            if tot == 1:
                # exit long position
                data.at[index, 'signal'] = -1
            elif tot == -1:
                # exit short position
                data.at[index, 'signal'] = 1
            tot = 0
    

    return data

time_frame = "3m"
# Load data
data = get_data(time_frame)

# Apply EMA crossover strategy
data = ema_crossover(data)

# Save to CSV
data.to_csv("../logs/ema_crossover_" + time_frame + ".csv")