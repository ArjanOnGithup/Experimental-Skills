import matplotlib.pyplot as plt
import ipywidgets as widgets
from ipywidgets import HBox, VBox
from ..ui.LineHandler import LineHandler, AreaHandler, DraggableVLine

def spectHRplot(data, x_min=None, x_max=None):
    """
    Create an interactive plot for ECG and breathing rate data.
    """

    # Set default x-axis limits if not provided
    x_min = x_min if x_min is not None else data.ecg.time.min()
    x_max = x_max if x_max is not None else data.ecg.time.max()

    # Create figure and axes based on available data
    fig, ax_ecg, ax_br = create_figure_axes(data)

    # Initialize LineHandler and AreaHandler for interactive manipulation
    line_handler = LineHandler(    
        callback_add=lambda line: print(f"Added line at x={line.line.get_xdata()}"),
        callback_remove=lambda line: print(f"Removed line at x={line.line.get_xdata()}"),
        callback_drag=lambda line, x: print(f"Dragged line to x={x}")
    )
    
    area_handler = AreaHandler(
        ax_ecg,
        callback_del  = lambda range: print(f"Deleting range: {range}"),
        callback_find = lambda range: print(f"Finding in range: {range}")
    )
    
    def update_plot(x_min, x_max):
        """update plot with current axis limits. """
        ax_ecg.set_xlim(x_min, x_max)
        print(f'adjusting the limits to {x_min} and {x_max}')
        fig.canvas.draw_idle()
         
    def plot():
        """plot with current data and axis limits. """
        # Plot ECG signal
        plot_ecg_signal(ax_ecg, data.ecg.time, data.ecg.level)
        ax_ecg.set_xlim(x_min, x_max)
        # Plot RTopTimes if available and manage vertical lines
        if hasattr(data.ecg, 'RTopTimes'):
            for rtop in data.ecg.RTopTimes:
                if x_min <= rtop <= x_max:
                    line_handler.add_line(ax_ecg, rtop)

        # Set ECG plot properties
        set_ecg_plot_properties(ax_ecg, x_min, x_max)

        if ax_br is not None and data.br is not None:
            plot_breathing_rate(ax_br, data.br, x_min, x_max)
        
        fig.canvas.draw_idle()

    # Widget and navigation setup
    control_box = create_widgets(data, x_min, x_max, update_plot, line_handler)
    plot()  # Initial plot update
    display(control_box)


def create_figure_axes(data):
    """ Helper function to create figure and axes. """
    if data.br is not None:
        fig, (ax_ecg, ax_br) = plt.subplots(2, 1, figsize=(12, 8),
                                            sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    else:
        fig, ax_ecg = plt.subplots(figsize=(12, 6))
        ax_br = None
    return fig, ax_ecg, ax_br


def plot_ecg_signal(ax, ecg_time, ecg_level):
    """ Plot the ECG signal on the provided axis. """
    ax.clear()
    ax.plot(ecg_time, ecg_level, label='ECG Signal', color='blue')


def set_ecg_plot_properties(ax, x_min, x_max):
    """ Set properties for the ECG plot. """
    ax.set_title('ECG Signal')
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('ECG Level (mV)')
    ax.set_xlim(x_min, x_max)
    ax.grid(True)


def plot_breathing_rate(ax, br_data, x_min, x_max):
    """ Plot breathing rate data. """
    ax.clear()
    ax.plot(br_data.time, br_data.level, label='Breathing Signal', color='green')
    ax.set_ylabel('Breathing Level')
    ax.grid(True)


def create_widgets(data, x_min, x_max, update_plot, line_handler):
    """ Create and configure the widget controls for navigation and mode selection. """

    # Navigation functions
    def zoom_in(b):
        nonlocal x_min, x_max
        x_min, x_max = adjust_x_limits(data.ecg.time, x_min, x_max, zoom_factor=0.5)
        update_plot(x_min, x_max)

    def zoom_out(b):
        nonlocal x_min, x_max
        x_min, x_max = adjust_x_limits(data.ecg.time, x_min, x_max, zoom_factor=2)
        update_plot(x_min, x_max)

    def move_left(b):
        nonlocal x_min, x_max
        x_min, x_max = move_x_limits(data.ecg.time, x_min, x_max, direction='left')
        update_plot(x_min, x_max)

    def move_right(b):
        nonlocal x_min, x_max
        x_min, x_max = move_x_limits(data.ecg.time, x_min, x_max, direction='right')
        update_plot(x_min, x_max)

    # Create buttons
    zoom_in_button = widgets.Button(description="Zoom In")
    zoom_out_button = widgets.Button(description="Zoom Out")
    move_left_button = widgets.Button(description="Move Left")
    move_right_button = widgets.Button(description="Move Right")

    # Assign button callbacks
    zoom_in_button.on_click(zoom_in)
    zoom_out_button.on_click(zoom_out)
    move_left_button.on_click(move_left)
    move_right_button.on_click(move_right)

    button_box = HBox([zoom_in_button, zoom_out_button, move_left_button, move_right_button])

    # Create radio buttons for interaction mode selection
    mode_radio_buttons = widgets.RadioButtons(
        options=['drag', 'add', 'find', 'remove'],
        description='Mode:',
        disabled=False
    )

    # Link radio button selection to LineHandler mode
    mode_radio_buttons.observe(lambda change: line_handler.update_mode(change), names='value')

    # Combine all controls in a vertical box
    return VBox([mode_radio_buttons, button_box])


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
