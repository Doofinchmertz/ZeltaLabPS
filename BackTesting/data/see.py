import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from fpdf import FPDF

df = pd.read_csv('btcusdt_3m_train.csv')
datetime_values = df.loc[(df['high'] - df['low']) / df['open'] >= pd.Series((df['high'] - df['low']) / df['open']).quantile(0.99), 'datetime']
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
    fig.write_image(f"plots/{idx}.png")

# Create a PDF object
pdf = FPDF()

# Directory to save the images
image_dir = "plots"

# Loop through the images in the directory
for filename in os.listdir(image_dir):
    if filename.endswith(".png"):
        # Add a new page to the PDF
        pdf.add_page()
        
        # Set the image position and size
        pdf.image(os.path.join(image_dir, filename), x=10, y=10, w=190)
        
# Save the PDF file
pdf.output("image_report.pdf", "F")
    
    