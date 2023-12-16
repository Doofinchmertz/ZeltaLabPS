import sys
import warnings

import numpy as np
import pandas as pd
import talib

warnings.filterwarnings('ignore')

# upper_treshold = 59
# lower_treshold = 32

# upper_treshold = 74
# lower_treshold = 24
# period = 12

upper_treshold_mfi = int(sys.argv[1])
lower_treshold_mfi = int(sys.argv[2])
upper_treshold_natr = int(sys.argv[3])
lower_treshold_natr = int(sys.argv[4])
period_mfi = int(sys.argv[5] )
period_natr = int(sys.argv[6])

# upper_treshold_mfi = int(70)
# lower_treshold_mfi = int(30)
# upper_treshold_natr = 0.87
# lower_treshold_natr = 0.23
# period_mfi = int(14)
# period_natr = int(14)
# # exit = int(sys.argv[7])
exit = 10

# df = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\data\data\btcusdt_1h_train.csv")
df1 = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\dataset\train\btcusdt_1h_train.csv")
df2 = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\dataset\test\btcusdt_1h_test.csv")

df = pd.concat([df1, df2], ignore_index=True)
df = df.reset_index(drop=True)

# df = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\src\Ayush\data.csv")

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
df['MFI'] = money_flow_index(df, period = period_mfi)
df['NATR'] = talib.CMO(df['close'], timeperiod = period_natr)

df['flag_mfi'] = df['MFI'].apply(lambda x: 1 if x > upper_treshold_mfi else (-1 if x < lower_treshold_mfi else 0))
df['flag_natr'] = df['NATR'].apply(lambda x: 1 if x > upper_treshold_natr else (-1 if (x > lower_treshold_natr and x < 2 * lower_treshold_natr) else 0))

def generate_signals_mfi(df, flag_column, signal_name, exit=exit):
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
            if counter < exit:
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

    df[signal_name] = signals

# Example Usage:
# Assuming you have a DataFrame named 'df' with columns 'log' and 'flag'

generate_signals_mfi(df, 'flag_natr', 'signal_natr', exit=exit)
generate_signals_mfi(df, 'flag_mfi', 'signal_mfi', exit=exit)

compare = 0
df['signal'] = np.nan
for i in range(len(df)):
    natr_signal = df['signal_natr'].iloc[i]
    mfi_signal = df['signal_mfi'].iloc[i]

    # Opening a trade
    if natr_signal == 1 and mfi_signal in [1, 0] and compare == 0:
        df['signal'].iloc[i] = 1
        compare = 1
    elif natr_signal == -1 and mfi_signal in [-1, 0] and compare == 0:
        df['signal'].iloc[i] = -1
        compare = -1
    elif natr_signal == 0 and mfi_signal == 1 and compare == 0:
        df['signal'].iloc[i] = 1
        compare = 1
    elif natr_signal == 0 and mfi_signal == -1 and compare == 0:
        compare = -1
        df['signal'].iloc[i] = -1

    # Closing a trade
    elif natr_signal == -1 and mfi_signal == 1 and compare == 1:
        df['signal'].iloc[i] = 0
        compare = 1
    elif natr_signal == 1 and mfi_signal == -1 and compare == 1:
        df['signal'].iloc[i] = 0
        compare = 1
    elif natr_signal == -1 and mfi_signal in [0, 1] and compare == 1:
        df['signal'].iloc[i] = -1
        compare = 0
    elif natr_signal == 1 and mfi_signal in [0, -1] and compare == 1:
        df['signal'].iloc[i] = 0
        compare = 1
    elif natr_signal == 0 and mfi_signal == 1 and compare == 1:
        df['signal'].iloc[i] = 0
        compare = 1
    elif natr_signal == 0 and mfi_signal == -1 and compare == 1:
        df['signal'].iloc[i] = -1
        compare = 0

df['signal'] = df['signal'].fillna(0)

df.to_csv(rf"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\src\logs\mfi_natr_{upper_treshold_mfi}_{lower_treshold_mfi}_{upper_treshold_natr}_{lower_treshold_natr}_{period_mfi}_{period_natr}.csv")