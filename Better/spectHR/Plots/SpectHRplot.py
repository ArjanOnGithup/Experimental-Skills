import matplotlib.pyplot as plt
import ipywidgets as widgets
import ipyvuetify as v
from ..ui.LineHandler import LineHandler, AreaHandler
import numpy as np


def spectHRplot(data, x_min=None, x_max=None):
    """
    Create an interactive plot for ECG and breathing rate data.
    """
    v.theme.dark = False
    plt.ion()
    # Set default x-axis limits if not provided
    x_min = x_min if x_min is not None else data.ecg.time.min()
    x_max = x_max if x_max is not None else data.ecg.time.max()

    # Create figure and axes based on available data
    fig, ax_ecg, ax_br = create_figure_axes(data)
    plt.figure(fig.number)
    
    # Initialize LineHandler for interactive line manipulation
    def update_rtop_times(line, new_x):
        # Find the line's index in the dataset (assumes unique x positions initially)
        print(f'Rtops: {len(data.ecg.RTopTimes)}')
        idx = line_handler.draggable_lines.index(line)  # Adjust if using unique identifiers
        data.ecg.RTopTimes[idx] = new_x  # Update original data's RTopTimes list
        print(f'Rtops: {len(data.ecg.RTopTimes)}')

        print(f'line: {idx} - {new_x}')

    # Initialize LineHandler with the callback
    line_handler = LineHandler(fig, ax_ecg, callback_drag=update_rtop_times)
    area_handler = AreaHandler(fig, ax_ecg)
    
       
    def update_plot(x_min, x_max):
        """ Update the plot with current data and axis limits. """
        plot_ecg_signal(ax_ecg, data.ecg.time, data.ecg.level)
        # Plot RTopTimes if available
        if hasattr(data.ecg, 'RTopTimes'):
            plot_rtop_times(ax_ecg, data.ecg.RTopTimes, x_min, x_max, line_handler)

        # Set ECG plot properties
        set_ecg_plot_properties(ax_ecg, x_min, x_max)

        if ax_br is not None and data.br is not None:
            plot_breathing_rate(ax_br, data.br.time, data.br.level, x_min, x_max, line_handler)

        fig.canvas.draw_idle()

    # Widget and navigation setup
    control_box = create_widgets(data, x_min, x_max, update_plot, line_handler)
    update_plot(x_min, x_max)  # Initial plot update
    display(control_box)
    # return fig, (ax_ecg, ax_br), control_box


def create_figure_axes(data):
    """ Helper function to create figure and axes. """
    if data.br is not None:
        fig, (ax_ecg, ax_br) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    else:
        fig, ax_ecg = plt.subplots(figsize=(12, 6))
        ax_br = None
    return fig, ax_ecg, ax_br

def plot_ecg_signal(ax, ecg_time, ecg_level):
    """ Plot the ECG signal on the provided axis. """
    ax.clear()
    ax.plot(ecg_time, ecg_level, label='ECG Signal', color='blue')


def plot_rtop_times(ax, rtop_times, x_min, x_max, line_handler):
    """ Plot vertical lines for R-top times within the current view. """
    for rtop in rtop_times:
        if x_min <= rtop <= x_max:
            line_handler.add_line(ax, rtop, color='r')


def set_ecg_plot_properties(ax, x_min, x_max):
    """ Set properties for the ECG plot. """
    ax.set_title('ECG Signal')
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('ECG Level (mV)')
    ax.set_xlim(x_min, x_max)
    ax.grid(True)


def plot_breathing_rate(ax, br_time, br_level):
    """ Plot breathing rate data. """
    ax.clear()
    ax.plot(br_time, br_level, label='Breathing Signal', color='green')
    ax.set_ylabel('Breathing Level')
    ax.grid(True)

def create_widgets(data, x_min, x_max, update_plot, line_handler):
    """ Create and configure the widget controls for navigation and mode selection. """

    # Navigation functions
    def zoom_in(*args):
        nonlocal x_min, x_max
        x_min, x_max = adjust_x_limits(data.ecg.time, x_min, x_max, zoom_factor=0.5)
        update_plot(x_min, x_max)

    def zoom_out(*args):
        nonlocal x_min, x_max
        x_min, x_max = adjust_x_limits(data.ecg.time, x_min, x_max, zoom_factor=2)
        update_plot(x_min, x_max)

    def move_right(*args):
        nonlocal x_min, x_max
        x_min, x_max = move_x_limits(data.ecg.time, x_min, x_max, direction='left')
        update_plot(x_min, x_max)

    def move_left(*args):
        nonlocal x_min, x_max
        x_min, x_max = move_x_limits(data.ecg.time, x_min, x_max, direction='right')
        update_plot(x_min, x_max)
        
    def set_mode(widget, event, data):
        line_handler.update_mode(data)
              
    # Create buttons
    zoom_in_button = v.Btn(color='primary',  class_='ma-2', children = ["Zoom In"])
    zoom_out_button = v.Btn(color='primary',  class_='ma-2', children = ["Zoom Out"])
    move_left_button = v.Btn(color='primary',  class_='ma-2', children = ["Move Left"])
    move_right_button = v.Btn(color='primary',  class_='ma-2', children = ["Move Right"])

    # Assign button callbacks
    zoom_in_button.on_event('click', zoom_in)
    zoom_out_button.on_event('click', zoom_out)
    move_left_button.on_event('click', move_left)
    move_right_button.on_event('click', move_right)

    button_box = v.Layout(children = [zoom_in_button, zoom_out_button, move_left_button, move_right_button])
    mode_select = v.Select(model="value", label = 'Mode:', items = ['Drag', 'Add', 'Find', 'Remove'])
    mode_select.on_event('change', set_mode)
    
    # Link radio button selection to LineHandler mode
    #mode_radio_buttons.observe(lambda change: line_handler.update_mode(change), names='value')

    # Combine all controls in a vertical box
    #return v.Layout(children = [mode_select, button_box])
    return v.Container(children = [v.Row( children = [v.Col(cols = 4, children = [mode_select]), v.Col(cols = 1, children = [button_box])])])

def adjust_x_limits(time_data, x_min, x_max, zoom_factor=1):
    """ Adjust the x-axis limits for zooming in/out. """
    x_center = (x_min + x_max) / 2
    x_range = (x_max - x_min) * zoom_factor
    x_min = max(0, x_center - x_range / 2)
    x_max = min(time_data.max(), x_center + x_range / 2)
    return x_min, x_max


def move_x_limits(time_data, x_min, x_max, direction='left'):
    """ Move the x-axis limits left or right. """
    move_amount = (x_max - x_min) / 4
    if direction == 'left':
        x_min = max(0, x_min - move_amount)
        x_max = min(time_data.max(), x_max - move_amount)
    else:
        x_min = max(0, x_min + move_amount)
        x_max = min(time_data.max(), x_max + move_amount)
    return x_min, x_max
