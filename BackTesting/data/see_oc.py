import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df = pd.read_csv('btcusdt_3m_train.csv')
datetime_values = df.loc[abs(df['open'] - df['close']) / df['open'] >= pd.Series(abs(df['open'] - df['close']) / df['open']).quantile(0.99), 'datetime']
for datetime in datetime_values :
    idx = df.loc[df['datetime'] == datetime].index.values[0]  # Get the index of the datetime
    selected_data = df[max(idx-30, 0):min(idx + 30, len(df))]  # Select 60 points around the datetime
    # Create subplots and mention plot grid size
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

    # Bar trace for volumes on 2nd row without legend
    volume_bar_trace = go.Bar(x=selected_data['datetime'], y=selected_data['volume'], showlegend=False)
    fig.add_trace(volume_bar_trace, row=2, col=1)
    

    # Do not show OHLC's rangeslider plot 
    fig.update(layout_xaxis_rangeslider_visible=False)
    
    # Save the plot as a PNG image
    fig.write_image(f"plots_oc/{idx}.png")

    
    