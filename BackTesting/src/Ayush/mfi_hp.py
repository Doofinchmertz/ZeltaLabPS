import pandas as pd
import numpy as np
import talib
import warnings
import sys
warnings.filterwarnings('ignore')
from optimum_param import *

# upper_treshold = 59
# lower_treshold = 32

upper_treshold = 77
lower_treshold = 13
period = 10
exit = 13

## For parameter tuning
## Tuning was done on first 60 percent of data and then run on the entire 
# upper_treshold = int(sys.argv[1])
# lower_treshold = int(sys.argv[2])
# period = int(sys.argv[3])
# exit = int(sys.argv[4])

df1 = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\dataset\train\btcusdt_1h_train.csv")
df2 = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\dataset\test\btcusdt_1h_test.csv")
df3 = pd.read_csv(r"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\src\Ayush\data.csv")

df3.rename(columns={'date': 'datetime'}, inplace=True)
df3.rename(columns={'Volume USDT' : 'volume'}, inplace=True)
df4 = df3[['datetime', 'open', 'high', 'low', 'close', 'volume']]

df = pd.concat([df1, df2], ignore_index=True)
df = df.reset_index(drop=True)

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
df['MFI'] = money_flow_index(df, period=period)

df['flag_mfi'] = df['MFI'].apply(lambda x: 1 if x > upper_treshold else (-1 if x < lower_treshold else 0))

def generate_signals(df, flag_column, exit=exit):
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

    df['flag'] = signals


## Using a ATR based stop loss for risk management
period = 15
multiplier = 9

df["atr"] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
df["sl_thresh"] = multiplier*df["atr"]/df["close"]
df["sl_thresh"] = df["sl_thresh"].fillna(0)

## Using stop loss with adaptive threshold
def gen_logs_v2(df):

    exit_loss = 0
    disable_trading = 0
    # stop_loss = 0
    compare = 0
     #also your stop loss
    logs = []

    for i in range(len(df)):
        if df["flag"].iloc[i] == 1 and compare == 0:
            # No open trade, encouter buy singal
            exit_loss = 0
            buy_price = df["close"].iloc[i]
            thresh = -df["sl_thresh"].iloc[i]
            compare = 1
            logs.append(1)

        #Once we open a trade, we have to check in df_fine whether to exit or not

        elif (df["flag"].iloc[i] != -1 and compare == 1):
            # Current buy trade, encounter buy signal or no signal - do nothing, update stop loss
            logs.append(0)

            #calculate pnl, if we exit now
            sell_price = df["close"].iloc[i]
            exit_loss = (sell_price - buy_price)/buy_price 
            
            #exit trade, if the loss is higher than stop loss
            if exit_loss < thresh and disable_trading == 0:
                logs[-1] = -1
                # print(f"disable_trading in buy trade - stop loss: {disable_trading}")
                disable_trading = 1


        elif df["flag"].iloc[i] == -1 and compare == 1:
            # Current buy trade, encounter sell signal
            #exit trade
            logs.append(-1)
            compare = 0
            exit_loss = 0

            #if trade was already exited before, check for disable trading flag here, do nothing here
            if disable_trading == 1:
                disable_trading = 0
                # print(f"disable_trading in buy trade - while exiting: {disable_trading}")
                # logs[-1] = 0
                compare = -1

        #SHORT TRADES
        elif df["flag"].iloc[i] == -1 and compare == 0:
            # No open trade, enounter sell siganl 
            exit_loss = 0
            sell_price = df["close"].iloc[i]
            thresh = -df["sl_thresh"].iloc[i]
            compare = -1
            logs.append(-1)

        elif (df["flag"].iloc[i] != 1 and compare == -1):
            # Current sell trade, encounter sell signal or no signal - do nothing, update stop loss
            logs.append(0)

            #calculate pnl, if we exit now
            buy_price = df["close"].iloc[i]
            exit_loss = (sell_price - buy_price)/sell_price 
            #exit trade, if the loss is higher than stop loss
            if exit_loss < thresh and disable_trading == 0:
                logs[-1] = 1
                # print(f"disable_trading in sell trade - stop loss: {disable_trading}")
                # print(i)
                disable_trading = 1

        elif df["flag"].iloc[i] == 1 and compare == -1:
            # 
            # print("Current sell trade, encounter buy signal")
            # print(f"{disable_trading}")
            #exit trade
            logs.append(1)
            compare = 0
            exit_loss = 0
            #if trade was already exited before, check for disable trading flag here, do nothing here
            if disable_trading == 1:
                # print("Check")
                disable_trading = 0
                # logs[-1] = 0
                compare = 1

        elif df["flag"].iloc[i] == 0 and compare == 0:
            logs.append(0)

    # Fill in any missing values in the new column with 0.
    # df['logs'].fillna(0, inplace=True)

    #close out positions (if needed)
    
    logs = np.array(logs)

    if logs[-1] != 0 and np.sum(logs) != 0:
        logs[-1] = 0
    elif logs[-1] != 0 and np.sum(logs) == 0:
        pass
    else:
        logs[-1] = -np.sum(logs)

    df["logs"] = logs

    return df
# Example Usage:
# Assuming you have a DataFrame named 'df' with columns 'log' and 'flag'

# saves the logs
generate_signals(df, 'flag_mfi', exit=exit)
gen_logs_v2(df)
df["signals"] = df["logs"]

# df.to_csv(rf"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\src\logs\mfi_{upper_treshold}_{lower_treshold}_{period}_{exit}.csv")
df.to_csv(rf"C:\Users\ayush\Desktop\IITB\ZeltaLabPS\BackTesting\src\logs\mfi2.csv")