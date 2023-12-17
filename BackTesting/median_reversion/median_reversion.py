import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import talib
import os
import random
from collections import deque

def plots_candlestick(df, entry_idx, exit_idx, starting_position, title):
    # Create subplots and mention plot grid size
        lookback = 20
        selected_data = df.loc[max(0,entry_idx-lookback):min(df.shape[0],exit_idx+lookback)]
        datetime = df['datetime'].iloc[entry_idx]
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    vertical_spacing=0.03, subplot_titles=(datetime, 'Volume'), 
                    row_width=[0.2, 0.7])

        # Plot OHLC on 1st row
        candlestick_trace = go.Candlestick(x=selected_data['datetime'],
                                            open=selected_data['open'],
                                            high=selected_data['high'],
                                            low=selected_data['low'],
                                            close=selected_data['close'])
        # fig.add_trace(candlestick_trace, row=1, col=1)

        # also add close price line curve on 1st row
        close_line_trace = go.Scatter(x=selected_data['datetime'], y=selected_data['close'], showlegend=True, name='Close Price')
        fig.add_trace(close_line_trace, row=1, col=1)

        # also add median line curve on 1st row
        median_line_trace = go.Scatter(x=selected_data['datetime'], y=selected_data['median'], showlegend=True, name='Median')
        fig.add_trace(median_line_trace, row=1, col=1)

        # also add median + REVERSION_THRESH*std line curve on 1st row
        median_plus_reversion_thresh_line_trace = go.Scatter(x=selected_data['datetime'], y=selected_data['median'] + selected_data['std']*REVERSION_THRESH, showlegend=True, name='Median + REVERSION_THRESH*std')
        fig.add_trace(median_plus_reversion_thresh_line_trace, row=1, col=1)

        # also add median - REVERSION_THRESH*std line curve on 1st row
        median_minus_reversion_thresh_line_trace = go.Scatter(x=selected_data['datetime'], y=selected_data['median'] - selected_data['std']*REVERSION_THRESH, showlegend=True, name='Median - REVERSION_THRESH*std')
        fig.add_trace(median_minus_reversion_thresh_line_trace, row=1, col=1)

        # also add DDI line curve on 1nd row with separate y-axis
        ddi_line_trace = go.Scatter(x=selected_data['datetime'], y=selected_data['DDI'], showlegend=True, name='DDI')
        fig.add_trace(ddi_line_trace, row=2, col=1)

        
        # Bar trace for volumes on 2nd row without legend
        volume_bar_trace = go.Bar(x=selected_data['datetime'], y=selected_data['volume'], showlegend=False)
        fig.add_trace(volume_bar_trace, row=2, col=1)

        # show legend for close price and median line curve on 1st row
        # fig.update_layout(showlegend=True, legend=dict(x=0.02, y=0.98))


        # add title as entry time and exit time and whether it is long / short
        # long if starting position is 1 and short if starting position is -1
        fig.update_layout(title_text=f"{'Long' if starting_position == 1 else 'Short'}" + title, title_x=0.5, title_font_size=20, title_font_color="black", title_font_family="Courier New")


        # add vertical line for entry and exit
        fig.add_vline(x=df['datetime'].iloc[entry_idx], line_width=1, line_dash="dash", line_color="green", row=1, col=1)
        fig.add_vline(x=df['datetime'].iloc[exit_idx], line_width=1, line_dash="dash", line_color="red", row=1, col=1)
        # Do not show OHLC's rangeslider plot 
        fig.update(layout_xaxis_rangeslider_visible=False)
        
        # Save the plot as a PNG image
        fig.write_image(f"plots/{str(datetime)}.png")
        # save as html
        fig.write_html(f"htmls/{str(datetime)}.html")

def clear_folders():
    plots_folder = "plots"
    htmls_folder = "htmls"

    # Clear plots folder
    for filename in os.listdir(plots_folder):
        file_path = os.path.join(plots_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Clear htmls folder
    for filename in os.listdir(htmls_folder):
        file_path = os.path.join(htmls_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

clear_folders()

df = pd.read_csv("../data/btcusdt_3m_diamond.csv")


MEDIAN_WINDOW = 40

REVERSION_THRESH = 2
TREND_THRESH = 3
STOPLOSS = .09
PROFIT_CAP = 0.02
MIN_PROFIT_CAP = 0.004
MAX_TRADE_HOLD = 1800

PROFIT_CAP_MULTIPLIER = 0.05
STOPLOSS_MULTIPLIER = 0.11

DI_WINDOW = 15
DDI_REV_THRESH = 10
DDI_TREND_THRESH = 50

PROFIT_LOSS_WINDOW = 25

q = deque(maxlen=PROFIT_LOSS_WINDOW)

df['median'] = df['close'].rolling(MEDIAN_WINDOW).median().shift(1)
df['std'] = df['close'].rolling(MEDIAN_WINDOW).std().shift(1)
df['PLUS_DI'] = talib.PLUS_DI(df.high, df.low, df.close, timeperiod=DI_WINDOW)
df['MINUS_DI'] = talib.MINUS_DI(df.high, df.low, df.close, timeperiod=DI_WINDOW)
df['DDI'] = df['PLUS_DI'] - df['MINUS_DI']

df['indicator'] = 0
df['signal'] = 0
tot = 0

current_position = 0
entry_idx = None
exit_idx = None

count = 0
entry_title = ""
exit_title = ""
sl_exits = 0
pc_exits = 0
max_hold_exits = 0
for i in range(MEDIAN_WINDOW, len(df)):
    if current_position == 0: # TRADE ENTRY
        # 
        # if abs(df['DDI'][i]) > 20:
        #     df.at[i, 'indicator'] = 0
        #     continue
        # 
        median = df['median'][i]
        std = df['std'][i]  
        # if df['close'][i] > median + std*TREND_THRESH:
        #     df.at[i, 'indicator'] = 1
        #     entry_title = "+TREND_THRESH"
        # elif df['close'][i] < median - std*TREND_THRESH:
        #     df.at[i, 'indicator'] = -1
        #     entry_title = "-TREND_THRESH"
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
        PROFIT_CAP = max(PROFIT_CAP_MULTIPLIER*q.count('P')/len(q), MIN_PROFIT_CAP) if len(q) >= PROFIT_LOSS_WINDOW else PROFIT_CAP
        STOPLOSS = STOPLOSS_MULTIPLIER*(len(q) - q.count('S'))/len(q) if len(q) >= PROFIT_LOSS_WINDOW else STOPLOSS

        PROFIT_CAP = PROFIT_CAP * (1 - (i - entry_idx)/MAX_TRADE_HOLD)
        STOPLOSS = STOPLOSS * (1 - (i - entry_idx)/MAX_TRADE_HOLD)

        PROFIT_CAP = max(PROFIT_CAP, MIN_PROFIT_CAP)

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
    
    if starting_position == 0 and current_position != 0:
        entry_idx = i
    elif starting_position != 0 and current_position == 0:
        exit_idx = i
        count += 1  
        if count%100 == 0:
            print(f"Plotting {count}th trade")
        # plots_candlestick(df, entry_idx, exit_idx, starting_position, entry_title + " " + exit_title)
        entry_idx = None
        exit_idx = None

print(f"sl_exits: {sl_exits}")
print(f"pc_exits: {pc_exits}")
print(f"max_hold_exits: {max_hold_exits}")
# print(f"pc_exits/sl_exits: {pc_exits/sl_exits}")
# print(f"SL_PROFIT_RATIO: {STOPLOSS/PROFIT_CAP}")

df.to_csv("../src/logs/median_reversion.csv")