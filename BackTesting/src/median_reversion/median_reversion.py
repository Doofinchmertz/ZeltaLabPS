import pandas as pd
import numpy as np

import talib

import random
from collections import deque
from utils import clear_folders, plots_candlestick
from optimal_constants import *
import argparse

# Clear folders before running the strategy
# clear_folders()

# Create an argument parser
parser = argparse.ArgumentParser(description='Median Reversion Strategy')

# Add the data filepath argument
parser.add_argument('--data', type=str, help='Path to the data file')

# Parse the command line arguments
args = parser.parse_args()

# Read the data from the CSV file
df = pd.read_csv(args.data)

# Create a deque to store the profit/loss history
q = deque(maxlen=PROFIT_LOSS_WINDOW)

# Calculate the rolling median and standard deviation
df['median'] = df['close'].rolling(MEDIAN_WINDOW).median().shift(1)
df['std'] = df['close'].rolling(MEDIAN_WINDOW).std().shift(1)

# Calculate the PLUS_DI and MINUS_DI indicators using talib
df['PLUS_DI'] = talib.PLUS_DI(df.high, df.low, df.close, timeperiod=DI_WINDOW)
df['MINUS_DI'] = talib.MINUS_DI(df.high, df.low, df.close, timeperiod=DI_WINDOW)


# Calculate the DDI (Difference between PLUS_DI and MINUS_DI)
df['DDI'] = df['PLUS_DI'] - df['MINUS_DI']

# Initialize the indicator and signal columns
df['indicator'] = 0
df['signal'] = 0

# Initialize variables for tracking trades
current_position = 0
entry_idx = None
exit_idx = None

# Initialize counters for different types of exits
sl_exits = 0
pc_exits = 0
max_hold_exits = 0
tot = 0
count = 0

# Iterate over the data
for i in range(MEDIAN_WINDOW, len(df)):
    if current_position == 0: # TRADE ENTRY
        # Check for different entry conditions
        median = df['median'][i]
        std = df['std'][i]  
        if df['DDI'][i] < DDI_REV_THRESH and df['DDI'][i] > -DDI_REV_THRESH:
            if df['close'][i] < median - std*REVERSION_THRESH:
                df.at[i, 'indicator'] = 1
                entry_title = "-REVERSION_THRESH"
            elif df['close'][i] > median + std*REVERSION_THRESH:
                df.at[i, 'indicator'] = -1
                entry_title = "+REVERSION_THRESH"
            else:
                df.at[i, 'indicator'] = 0
        elif df['DDI'][i] > DDI_TREND_THRESH and df['volume'][i] > df['volume'][i-1] and df['close'][i] > median + std*TREND_THRESH:
            df.at[i, 'indicator'] = 1
            entry_title = "+DDI_TREND_THRESH"
        elif df['DDI'][i] < -DDI_TREND_THRESH and df['volume'][i] > df['volume'][i-1] and df['close'][i] < median - std*TREND_THRESH:
            df.at[i, 'indicator'] = -1
            entry_title = "-DDI_TREND_THRESH"
    else: # TRADE EXIT
        # Calculate the profit cap and stop loss based on the trade duration
        PROFIT_CAP = max(PROFIT_CAP_MULTIPLIER*q.count('P')/len(q), MIN_PROFIT_CAP) if len(q) >= PROFIT_LOSS_WINDOW else PROFIT_CAP
        STOPLOSS = STOPLOSS_MULTIPLIER*(len(q) - q.count('S'))/len(q) if len(q) >= PROFIT_LOSS_WINDOW else STOPLOSS

        PROFIT_CAP = PROFIT_CAP * (1 - (i - entry_idx)/MAX_TRADE_HOLD)
        STOPLOSS = STOPLOSS * (1 - (i - entry_idx)/MAX_TRADE_HOLD)

        PROFIT_CAP = max(PROFIT_CAP, MIN_PROFIT_CAP)

        # Check for different exit conditions
        if i >= entry_idx + MAX_TRADE_HOLD:
            df.at[i, 'indicator'] = -1*current_position
            exit_title = "MAX_TRADE_HOLD"
            max_hold_exits += 1
            q.append('M')
        if current_position == 1:
            if df['close'][i] > df['close'][entry_idx]*(1+PROFIT_CAP):
                df.at[i, 'indicator'] = -1
                exit_title = "PROFIT_CAP"
                pc_exits += 1
                q.append('P')
            elif df['close'][i] < df['close'][entry_idx]*(1-STOPLOSS):
                df.at[i, 'indicator'] = -1
                exit_title = "STOPLOSS"
                sl_exits += 1
                q.append('S')
        elif current_position == -1:
            if df['close'][i] < df['close'][entry_idx]*(1-PROFIT_CAP):
                df.at[i, 'indicator'] = 1
                exit_title = "PROFIT_CAP"
                pc_exits += 1
                q.append('P')
            elif df['close'][i] > df['close'][entry_idx]*(1+STOPLOSS):
                df.at[i, 'indicator'] = 1
                exit_title = "STOPLOSS"
                sl_exits += 1
                q.append('S')
    
    starting_position = current_position

    # Update the current position based on the indicator
    if df['indicator'][i] == 1:
        if tot == 0 or tot == -1:
            # enter long position/exit short position
            tot += 1
            df.at[i, 'signal'] = 1
            current_position += 1
    elif df['indicator'][i] == -1:
        if tot == 0 or tot == 1:
            # enter short position/exit long position
            tot -= 1
            df.at[i, 'signal'] = -1
            current_position -= 1
    
    # Check for trade entry and exit points
    if starting_position == 0 and current_position != 0:
        entry_idx = i
    elif starting_position != 0 and current_position == 0:
        exit_idx = i
        count += 1  
        if count%100 == 0:
            print(f"Plotting {count}th trade")
        # Plot the trade
        # plots_candlestick(df, entry_idx, exit_idx, entry_title, exit_title, starting_position)
        entry_idx = None
        exit_idx = None

# Print the number of different types of exits
print(f"sl_exits: {sl_exits}")
print(f"pc_exits: {pc_exits}")
print(f"max_hold_exits: {max_hold_exits}")

# Save the modified dataframe to a CSV file
df.to_csv("logs/median_reversion.csv")