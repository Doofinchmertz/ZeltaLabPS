import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from optimal_constants import *

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
        fig.add_trace(candlestick_trace, row=1, col=1)

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
