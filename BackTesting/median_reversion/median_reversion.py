import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import talib
import os

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

df = pd.read_csv("../data/btcusdt_3m_train.csv")


MEDIAN_WINDOW = 20

REVERSION_THRESH = 2
STOPLOSS = .005
PROFIT_CAP = 0.01
MAX_TRADE_HOLD = 90
DI_WINDOW = 20

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
        if df['close'][i] < median - std*REVERSION_THRESH:
            df.at[i, 'indicator'] = 1
            entry_title = "-REVERSION_THRESH"
        elif df['close'][i] > median + std*REVERSION_THRESH:
            df.at[i, 'indicator'] = -1
            entry_title = "+REVERSION_THRESH"
        else:
            df.at[i, 'indicator'] = 0
    else: # TRADE EXIT
        if i >= entry_idx + MAX_TRADE_HOLD:
            df.at[i, 'indicator'] = -1*current_position
            exit_title = "MAX_TRADE_HOLD"
        if current_position == 1:
            if df['close'][i] > df['close'][entry_idx]*(1+PROFIT_CAP):
                df.at[i, 'indicator'] = -1
                exit_title = "PROFIT_CAP"
            elif df['close'][i] < df['close'][entry_idx]*(1-STOPLOSS):
                df.at[i, 'indicator'] = -1
                exit_title = "STOPLOSS"
        elif current_position == -1:
            if df['close'][i] < df['close'][entry_idx]*(1-PROFIT_CAP):
                df.at[i, 'indicator'] = 1
                exit_title = "PROFIT_CAP"
            elif df['close'][i] > df['close'][entry_idx]*(1+STOPLOSS):
                df.at[i, 'indicator'] = 1
                exit_title = "STOPLOSS"
    
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
        print(f"Plotting {count}th trade")
        # plots_candlestick(df, entry_idx, exit_idx, starting_position, entry_title + " " + exit_title)
        entry_idx = None
        exit_idx = None

df.to_csv("../src/logs/median_reversion.csv")