from bokeh.plotting import figure, show
from bokeh.models import WheelZoomTool, HoverTool
from bokeh.events import DoubleTap
import numpy as np

# Generate some example data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create a Bokeh figure
p = figure(title="Zoomable Plot", x_axis_label="X-axis", y_axis_label="Y-axis", tools="pan,box_zoom,reset")

# Add a line to the plot
line = p.line(x, y, line_width=2, legend_label="Data")

# Add hover tool
hover = HoverTool()
hover.tooltips = [("x", "@x"), ("y", "@y")]
p.add_tools(hover)

# Add wheel zoom tool
p.add_tools(WheelZoomTool())

# DoubleTap event handler to reset the plot
def reset_plot(event):
    p.x_range.reset_start()
    p.x_range.reset_end()
    p.y_range.reset_start()
    p.y_range.reset_end()

p.on_event(DoubleTap, reset_plot)

# Show the plot
show(p)
