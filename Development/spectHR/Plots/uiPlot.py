import matplotlib.pyplot as plt
import matplotlib.patches as patches
import ipywidgets as widgets
from IPython.display import display

# Initialize variables
x_min, x_max = 0, 10  # Example initial limits
dragging = False
drag_start_x = None

# Functions to handle mode updates and navigation
def update_mode(change):
    global drag_mode
    drag_mode = change.new

def on_prev_clicked(change):
    update_plot(x_min - 10, x_max - 10)

def on_next_clicked(change):
    update_plot(x_min + 10, x_max + 10)

# Functions for interactive drag events
def on_press(event):
    global dragging, drag_start_x
    if event.inaxes == ax_ecg:
        dragging = True
        drag_start_x = event.xdata

def on_drag(event):
    if dragging and event.inaxes == ax_ecg:
        drag_end_x = event.xdata
        update_zoom_region(drag_start_x, drag_end_x)

def on_release(event):
    global dragging
    if dragging and event.inaxes == ax_ecg:
        dragging = False
        handle_zoom_release(drag_start_x, event.xdata)

# Function to update zoom region
def update_zoom_region(start_x, end_x):
    x_min_zoom, x_max_zoom = min(start_x, end_x), max(start_x, end_x)
    positional_patch.set_x(x_min_zoom)
    positional_patch.set_width(x_max_zoom - x_min_zoom)
    fig.canvas.draw_idle()

# Function to handle zoom release actions
def handle_zoom_release(start_x, end_x):
    global x_min, x_max
    x_min, x_max = min(start_x, end_x), max(start_x, end_x)
    update_plot(x_min, x_max)

# Plotting and figure setup
def create_figure_axes(data):
    fig, (ax_overview, ax_ecg, ax_br) = plt.subplots(3, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 4, 1]})
    ax_ecg.plot(data.ecg.time, data.ecg.level, color='blue')
    ax_overview.plot(data.ecg.time, data.ecg.level, color='grey', alpha=0.5)
    if hasattr(data, 'br'):
        ax_br.plot(data.br.time, data.br.level, color='green')
    ax_overview.set_xlim(data.ecg.time[0], data.ecg.time[-1])
    return fig, ax_ecg, ax_overview, ax_br

def plot_overview(ax_overview, time, level, x_min, x_max):
    patch = patches.Rectangle((x_min, ax_overview.get_ylim()[0]), x_max - x_min, ax_overview.get_ylim()[1], alpha=0.3)
    ax_overview.add_patch(patch)
    return patch

# Update plot with new x-axis range
def update_plot(x_min, x_max):
    ax_ecg.set_xlim(x_min, x_max)
    positional_patch.set_x(x_min)
    positional_patch.set_width(x_max - x_min)
    fig.canvas.draw_idle()

# Widget and UI setup
dropdown = widgets.Dropdown(
    options=['drag', 'add', 'del', 'find'],
    value='drag',
    description='Mode:',
    disabled=False,
)
dropdown.observe(update_mode, 'value')

btn_prev = widgets.Button(description="Previous")
btn_prev.on_click(on_prev_clicked)

btn_next = widgets.Button(description="Next")
btn_next.on_click(on_next_clicked)

# Create the main figure and subplots for ECG and breathing data
fig, ax_ecg, ax_overview, ax_br = create_figure_axes(data)

# Initialize the line handler for interactive lines
line_handler = LineHandler(ax_ecg)

# Initialize positional patch for draggable zoom region in the overview plot
positional_patch = plot_overview(ax_overview, data.ecg.time, data.ecg.level, x_min, x_max)

# Initialize drag state variables
drag_mode = None
initial_xmin, initial_xmax = None, None

# Connect event handlers
fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_drag)
fig.canvas.mpl_connect('button_release_event', on_release)

# Set initial plot range and render the ECG and optional breathing data
update_plot(x_min, x_max)

# Display the widgets and figure
display(widgets.HBox([btn_prev, btn_next, dropdown]))
display(fig)