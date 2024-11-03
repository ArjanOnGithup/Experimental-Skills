import matplotlib.pyplot as plt
import matplotlib.patches as patches
import ipyvuetify as v
from ..ui.LineHandler import LineHandler, AreaHandler
import numpy as np
from IPython.display import display

def spectHRplotM(data, x_min=None, x_max=None):
    """
    Create an interactive plot for ECG and breathing rate data.
    """
    v.theme.dark = True
    plt.ioff()

    # Set default x-axis limits if not provided
    x_min = x_min if x_min is not None else data.ecg.time.min()
    x_max = x_max if x_max is not None else data.ecg.time.max()

    # Create figure and axes based on available data
    fig, ax_ecg, ax_overview, ax_br = create_figure_axes(data)

    # Initialize LineHandler for interactive line manipulation
    def update_rtop_times(line, new_x):
        idx = line_handler.draggable_lines.index(line)  # Get index from the handler
        data.ecg.RTopTimes[idx] = new_x  # Update the original data's RTopTimes list

    # Initialize LineHandler and AreaHandler
    line_handler = LineHandler(fig, ax_ecg, callback_drag=update_rtop_times)
    area_handler = AreaHandler(fig, ax_ecg)

    def update_plot(x_min, x_max):
        """ Update the plot with current data and axis limits. """
        plot_ecg_signal(ax_ecg, data.ecg.time, data.ecg.level)
        plot_overview(ax_overview, data.ecg.time, data.ecg.level, x_min, x_max)
        if hasattr(data.ecg, 'RTopTimes'):
            plot_rtop_times(ax_ecg, data.ecg.RTopTimes, x_min, x_max, line_handler)

        set_ecg_plot_properties(ax_ecg, x_min, x_max)

        if ax_br is not None and data.br is not None:
            plot_breathing_rate(ax_br, data.br.time, data.br.level, x_min, x_max, line_handler)

        fig.canvas.draw_idle()  # Refresh the canvas

    # Replace the FloatRangeSlider with v.Slider for ipyvuetify
    x_range_slider = v.RangeSlider(
        v_model=[x_min, x_max],
        min=data.ecg.time.min(),
        max=data.ecg.time.max(),
        step=0.1,
        class_="mt-4",
        style_='width: 100%'
    )

    slider_box = v.Row(children=[
        v.Flex(xs=2),  # Adds space on the left
        x_range_slider,  # The slider
        v.Flex(xs=1)  # Optional: Adds more space on the right if you want finer adjustment
    ], style_="width: 100%;")

    # Observe the range slider to update plot based on slider values
    def update_x_range(widget, event, data):
        nonlocal x_min, x_max
        x_min, x_max = widget.v_model
        update_plot(x_min, x_max)

    x_range_slider.on_event('change', update_x_range)

    # Replace Dropdown with v.Select for mode selection
    mode_select = v.Select(
        items=['Drag', 'Add', 'Find', 'Remove'],
        v_model='Drag',
        label="Mode",
        class_="mt-4"
    )

    # Link dropdown selection to LineHandler mode
    def update_mode(widget, event, data):
        line_handler.update_mode(widget.v_model)  # Update LineHandler mode

    mode_select.on_event('change', update_mode)

    # Use v.Container to arrange widgets in ipyvuetify
    control_box = v.Container(
        children=[
            mode_select,
            v.Html(tag="div", children=[fig.canvas]),  # Embed the matplotlib canvas
            slider_box
        ]
    )

    # Display the control box
    display(control_box)
    update_plot(x_min, x_max)  # Initial plot update

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
