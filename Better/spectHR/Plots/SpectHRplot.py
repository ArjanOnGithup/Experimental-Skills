import matplotlib.pyplot as plt
import matplotlib.patches as patches
import ipywidgets as widgets
import ipyvuetify as v
from ..ui.LineHandler import LineHandler, AreaHandler
import numpy as np

def spectHRplot(data, x_min=None, x_max=None):
    v.theme.dark = False
    plt.ioff()

    x_min = x_min if x_min is not None else data.ecg.time.min()
    x_max = x_max if x_max is not None else data.ecg.time.max()

    fig, ax_ecg, ax_overview, ax_br = create_figure_axes(data)

    def update_rtop_times(line, new_x):
        idx = line_handler.draggable_lines.index(line)
        data.ecg.RTopTimes[idx] = new_x

    # Initialize LineHandler and AreaHandler
    line_handler = LineHandler(fig, ax_ecg, callback_drag=update_rtop_times)
    area_handler = AreaHandler(fig, ax_ecg)

    def update_plot(x_min, x_max):
        plot_ecg_signal(ax_ecg, data.ecg.time, data.ecg.level)
        plot_overview(ax_overview, data.ecg.time, data.ecg.level, x_min, x_max)
        if hasattr(data.ecg, 'RTopTimes'):
            plot_rtop_times(ax_ecg, data.ecg.RTopTimes, x_min, x_max, line_handler)
        set_ecg_plot_properties(ax_ecg, x_min, x_max)
        if ax_br is not None and data.br is not None:
            plot_breathing_rate(ax_br, data.br.time, data.br.level, x_min, x_max, line_handler)
        fig.canvas.draw_idle()

    # Initialize the draggable patch on the overview axis
    patch = patches.Rectangle((x_min, ax_overview.get_ylim()[0]),
                              x_max - x_min, ax_overview.get_ylim()[1] - ax_overview.get_ylim()[0],
                              color='gray', alpha=0.3)
    ax_overview.add_patch(patch)

    # State variables to track dragging behavior
    drag_mode = None
    initial_xmin = x_min
    initial_xmax = x_max

    def on_press(event):
        print(f"pressed {event.x},{event.y}, {event.inaxes} ({ax_overview}) in: {patch.contains_point((event.x, event.y))}")
        nonlocal drag_mode, initial_xmin, initial_xmax
        if event.inaxes != ax_overview:
            return
        
        # Check if the event is within the patch's bounds
        if x_min <= event.xdata <= x_max:
            initial_xmin, initial_xmax = x_min, x_max

            # Determine drag mode based on cursor position
            if abs(event.xdata - x_min) < 0.1:      # Near left side
                drag_mode = 'left'
            elif abs(event.xdata - x_max) < 0.1:    # Near right side
                drag_mode = 'right'
            else:                                   # Center
                drag_mode = 'center'

        print(f'dragmode is {drag_mode}')
        
    def on_drag(event):
        nonlocal x_min, x_max
        if drag_mode is None or event.inaxes != ax_overview:
            return

        if drag_mode == 'left':
            x_min = min(event.xdata, x_max - 0.1)  # Ensure x_min < x_max
        elif drag_mode == 'right':
            x_max = max(event.xdata, x_min + 0.1)  # Ensure x_max > x_min
        elif drag_mode == 'center':
            dx = event.xdata - 0.5 * (initial_xmin + initial_xmax)
            x_min = initial_xmin + dx
            x_max = initial_xmax + dx

        # Update the patch and main plot with new limits
        update_plot(x_min, x_max)
        patch.set_x(x_min)
        patch.set_width(x_max - x_min)
        fig.canvas.draw_idle()

    def on_release(event):
        nonlocal drag_mode
        drag_mode = None  # Reset drag mode when mouse is released

    # Connect the patch drag events
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('motion_notify_event', on_drag)
    fig.canvas.mpl_connect('button_release_event', on_release)

    # Connect the LineHandler events (important to call after patch events are connected)
    line_handler.connect(fig)

    # Mode selection dropdown
    mode_select = widgets.Dropdown(
        options=['Drag', 'Add', 'Find', 'Remove'],
        value='Drag',
        description='Mode:',
        layout=widgets.Layout(width='200px')
    )

    def update_mode(change):
        line_handler.update_mode(change['new'])

    mode_select.observe(update_mode, names='value')

    control_box = widgets.VBox([mode_select, fig.canvas])
    display(control_box)
    update_plot(x_min, x_max)


def create_figure_axes(data):
    """ Helper function to create figure and axes. """
    if data.br is not None:
        fig, (ax_ecg, ax_overview, ax_br) = \
            plt.subplots(3, 1, figsize=(12, 8), sharex=True, \
                         gridspec_kw={'height_ratios': [4, 1, 3]})
        ax_ecg.get_shared_x_axes().join(ax_ecg.xaxis, ax_br.xaxis)
    else:
        fig, (ax_ecg, ax_overview) = \
            plt.subplots(2 ,1, figsize=(12, 8), sharex=False, \
                         gridspec_kw={'height_ratios': [6, 1]})
        ax_br = None
 
    return fig, ax_ecg, ax_overview, ax_br

def plot_ecg_signal(ax, ecg_time, ecg_level):
    """ Plot the ECG signal on the provided axis. """
    ax.clear()
    ax.plot(ecg_time, ecg_level, label='ECG Signal', color='blue')
 
def plot_overview(ax, ecg_time, ecg_level, x_min, x_max):
    """ Plot the ECG signal on the provided axis. """
    ax.clear()
    ax.plot(ecg_time, ecg_level, color='green')
    patch = patches.Rectangle((x_min, ax.get_ylim()[0]),
                                       x_max-x_min, ax.get_ylim()[1] - ax.get_ylim()[0],
                                       color='gray', alpha=0.3)
    ax.add_patch(patch)
 
    ax.yaxis.set_ticks([])  # Remove y-axis ticks
    ax.set_yticklabels([])   # Remove y-axis labels
    ax.spines['top'].set_visible(False)    # Hide the top spine
    ax.spines['right'].set_visible(False)  # Hide the right spine
    ax.spines['left'].set_visible(False)   # Hide the left spine
 

def plot_rtop_times(ax, rtop_times, x_min, x_max, line_handler):
    """ Plot vertical lines for R-top times within the current view. """
    for rtop in rtop_times:
        if x_min <= rtop <= x_max:
            line_handler.add_line(ax, rtop, color='r')  # Add a red line for R tops

def set_ecg_plot_properties(ax, x_min, x_max):
    """ Set properties for the ECG plot. """
    ax.set_title('ECG Signal')
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('ECG Level (mV)')
    ax.set_xlim(x_min, x_max)
    ax.grid(True)

def plot_breathing_rate(ax, br_time, br_level, x_min, x_max, line_handler):
    """ Plot breathing rate data. """
    ax.clear()
    ax.plot(br_time, br_level, label='Breathing Signal', color='green')
    ax.set_ylabel('Breathing Level')
    ax.grid(True)
