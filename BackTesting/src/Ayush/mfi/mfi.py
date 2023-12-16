import pandas as pd
import numpy as np
import talib
import warnings
import sys
warnings.filterwarnings('ignore')
from optimum_param import *
import argparse
from utils import *

parser = argparse.ArgumentParser(description="MFI Strategy")
parser.add_argument("--data", type = str,  help = "Path to data file", required = True)
args = parser.parse_args()
df = pd.read_csv(args.data)
df = df.reset_index(drop=True)

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
df['signals'] = df['logs']
generate_signals(df, 'flag_mfi', exit=exit)
gen_logs_v2(df)
df.to_csv(rf".\logs\mfi.csv")