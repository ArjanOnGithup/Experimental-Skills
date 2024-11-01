import numpy as np
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.layouts import column
from bokeh.io import output_notebook

# Output to Jupyter Notebook
output_notebook()

# Generate sine wave data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Detect peaks (where slope changes from positive to negative)
peaks_x = x[np.where((y[:-2] < y[1:-1]) & (y[1:-1] > y[2:]))[0] + 1]
peaks_y = y[np.where((y[:-2] < y[1:-1]) & (y[1:-1] > y[2:]))[0] + 1]

# Create data sources for sine wave and draggable lines
sine_source = ColumnDataSource(data={'x': x, 'y': y})
vlines_source = ColumnDataSource(data={'x': peaks_x, 'y_start': [-1] * len(peaks_x), 'y_end': [1] * len(peaks_x)})

# Create a plot
p = figure(width=700, height=400, title="Sine Wave with Draggable Vertical Lines at Peaks")
p.line('x', 'y', source=sine_source, line_width=2, color='blue', legend_label="Sine Wave")

# Add vertical lines at the peaks
vlines = p.segment('x', 'y_start', 'x', 'y_end', source=vlines_source, line_width=2, color="red")

# JavaScript callback to make the lines draggable
callback = CustomJS(args=dict(source=vlines_source), code="""
    const data = source.data;
    const x = data['x'];
    const y_start = data['y_start'];
    const y_end = data['y_end'];
    
    const drag_event = cb_obj;
    const delta = drag_event.deltaX / 100;  // scale the drag speed

    for (let i = 0; i < x.length; i++) {
        if (Math.abs(drag_event.startX - x[i]) < 0.1) {  // Adjust sensitivity as needed
            x[i] += delta;
        }
    }

    source.change.emit();
""")

# Attach the callback to the vertical lines (segments)
vlines.js_on_event("pan", callback)

# Show the plot
show(column(p))

