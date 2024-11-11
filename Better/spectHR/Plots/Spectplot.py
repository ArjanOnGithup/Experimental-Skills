import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
import ipywidgets as widgets
import math

from ..ui.LineHandler import LineHandler, AreaHandler
import numpy as np

def spectplot(data, x_min=None, x_max=None):
    """
    Plot the heart rate data with interactive features for zooming, 
    dragging lines, and selecting modes for adding, removing, or finding R-top times.

    Parameters:
    - data (object): A data object containing ECG and optional breathing (br) data.
    - x_min (float, optional): Minimum x-axis value for the ECG plot. Defaults to the minimum in data.
    - x_max (float, optional): Maximum x-axis value for the ECG plot. Defaults to the maximum in data.

    Interactive Features:
    - Draggable lines for R-top times (ECG peaks).
    - Adjustable zoom region using the overview plot.
    - Mode selection for dragging, adding, finding, or removing R-top times.
    """
    # Local Functions:
    
    def update_plot(x_min, x_max):
        """
        Redraw the ECG plot, R-top times, and breathing rate (if available).
        This function also adjusts the plot properties for the selected x-axis limits.

        Parameters:
        - x_min (float): Minimum x-axis limit for the zoomed view.
        - x_max (float): Maximum x-axis limit for the zoomed view.
        """
        
        plot_ecg_signal(ax_ecg, data.ecg.time, data.ecg.level)
        if hasattr(data.ecg, 'RTopTimes'):
            plot_rtop_times(ax_ecg, data.ecg.RTopTimes,line_handler)
        set_ecg_plot_properties(ax_ecg, x_min, x_max)
        if ax_br is not None and data.br is not None:
            plot_breathing_rate(ax_br, data.br.time, data.br.level, x_min, x_max, line_handler)
        fig.canvas.draw_idle()

    def on_press(event):
        """Handle mouse press event to initiate dragging on overview plot."""
        nonlocal drag_mode, initial_xmin, initial_xmax
        if event.inaxes != ax_overview:
            return

        # Check if the press is within the draggable patch bounds
        if x_min <= event.xdata <= x_max:
            initial_xmin, initial_xmax = x_min, x_max
            dist = x_max - x_min
            # Determine drag mode based on proximity to the edges
            if abs(event.xdata - x_min) < 0.3 * dist:
                drag_mode = 'left'
            elif abs(event.xdata - x_max) < 0.3 * dist:
                drag_mode = 'right'
            else:
                drag_mode = 'center'

    def on_drag(event):
        """Handle dragging of the patch to adjust the zoom region."""
        nonlocal x_min, x_max, drag_mode, initial_xmin, initial_xmax
        if drag_mode is None or event.inaxes != ax_overview:
            return

        # Adjust limits based on drag mode
        if drag_mode == 'left':
            x_min = min(event.xdata, x_max - 0.1)
        elif drag_mode == 'right':
            x_max = max(event.xdata, x_min + 0.1)
        elif drag_mode == 'center':
            dx = event.xdata - 0.5 * (initial_xmin + initial_xmax)
            x_min = initial_xmin + dx
            x_max = initial_xmax + dx

        # Update patch and plot properties
        positional_patch.set_x(x_min)
        positional_patch.set_width(x_max - x_min)
        fig.canvas.draw_idle()
   
    def on_release(event):
        """Reset dragging mode upon mouse release."""
        nonlocal drag_mode
        drag_mode = None
        set_ecg_plot_properties(ax_ecg, x_min, x_max)
        fig.canvas.draw_idle()

    def update_mode(change):
        """Update the mode in LineHandler based on dropdown selection."""
        line_handler.update_mode(change['new'])


    def create_figure_axes(data):
        """
        Create and return figure and axes for ECG and optional breathing data.

        Parameters:
        - data (object): Contains ECG and optional breathing data.

        Returns:
        - fig (Figure): Matplotlib figure containing all plots.
        - ax_ecg (Axes): Axis for the ECG signal plot.
        - ax_overview (Axes): Axis for the overview plot.
        - ax_br (Axes, optional): Axis for breathing rate if data is available.
        """
        if data.br is not None:
            fig, (ax_ecg, ax_overview, ax_br) = plt.subplots(
                3, 1, figsize=(12, 8), sharex=True,
                gridspec_kw={'height_ratios': [4, 1, 3]}
            )
        else:
            fig, (ax_ecg, ax_overview) = plt.subplots(
                2, 1, figsize=(12, 8), sharex=False,
                gridspec_kw={'height_ratios': [11, 1]}
            )
            ax_br = None

        return fig, ax_ecg, ax_overview, ax_br

    def plot_overview(ax, ecg_time, ecg_level, x_min, x_max):
        """Plot ECG overview with a shaded region representing the zoomed area."""
        ax.clear()
        ax.plot(ecg_time, ecg_level, color='green')
        ax.set_title('')
            # Initialize a draggable patch for the overview plot
        positional_patch = patches.Rectangle((x_min, ax.get_ylim()[0]),
                                  x_max - x_min, ax.get_ylim()[1] - ax.get_ylim()[0],
                                  color='blue', alpha=0.2, animated = False)

        ax.add_patch(positional_patch)
        ax.set_yticks([])  
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        return positional_patch

    def plot_rtop_times(ax, rtop_times, line_handler):
        """Plot vertical lines for R-top times within the current view."""
        line_handler.draggable_lines = []
        for rtop in rtop_times:
            line_handler.add_line(ax, rtop, color='blue')

    def set_ecg_plot_properties(ax, x_min, x_max):
        """Configure ECG plot properties."""
        r = data.ecg.level.max()-data.ecg.level.min()
        s = int(math.log10(abs(r)))

        ax.set_title('')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('ECG Level (mV)')
        ax.set_xlim(x_min, x_max)
        
        ax.xaxis.set_major_locator(MultipleLocator(1))  # Major ticks every 1 second
        ax.xaxis.set_minor_locator(MultipleLocator(0.2))  # Minor ticks every 0.2 seconds

        ax.yaxis.set_major_locator(MultipleLocator(math.pow(10,s))) 
        ax.yaxis.set_minor_locator(MultipleLocator(math.pow(10,s)/5))

        ax.xaxis.grid(which='minor', color='salmon', lw=0.3)
        ax.xaxis.grid(which='major', color='r', lw=0.7)
        ax.yaxis.grid(which='minor', color='salmon', lw=0.3)
        ax.yaxis.grid(which='major', color='r', lw=0.7)
        
        ax.grid(True)

    def plot_ecg_signal(ax, ecg_time, ecg_level):
        """Plot the ECG signal on the provided axis."""
        ax.plot(ecg_time, ecg_level, label='ECG Signal', color='red')

    def plot_breathing_rate(ax, br_time, br_level, x_min, x_max, line_handler):
        """Plot breathing rate data on a separate axis."""
        ax.clear()
        ax.plot(br_time, br_level, label='Breathing Signal', color='green')
        ax.set_ylabel('Breathing Level')
        ax.grid(True)
   
    # Main Plot: Configure theme
    plt.ioff()
    plt.title('')
    
    # Initialize x-axis limits based on input or data
    x_min = x_min if x_min is not None else data.ecg.time.min()
    x_max = x_max if x_max is not None else data.ecg.time.max()

    # Create figure and axis handles
    fig, ax_ecg, ax_overview, ax_br = create_figure_axes(data)
    fig.canvas.toolbar_visible = False
    fig.tight_layout()

    # Callback to update R-top times upon dragging a line
    def update_rtop_times(line, new_x):
        """Update the position of an R-top time after dragging."""
        idx = line_handler.draggable_lines.index(line)
        data.ecg.RTopTimes.iloc[idx] = new_x

    # Initialize LineHandler for managing R-top times and AreaHandler for shaded regions
    line_handler = LineHandler(fig, ax_ecg, callback_drag=update_rtop_times)
    area_handler = AreaHandler(fig, ax_ecg)
    
    positional_patch  = plot_overview(ax_overview, data.ecg.time, data.ecg.level,  x_min, x_max)

 
    # State variables for dragging
    drag_mode = None
    initial_xmin, initial_xmax = x_min, x_max
    # Connect the patch dragging events
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('motion_notify_event', on_drag)
    fig.canvas.mpl_connect('button_release_event', on_release)

    # Mode selection dropdown widget for interaction
    mode_select = widgets.Dropdown(
        options=['Drag', 'Add', 'Find', 'Remove'],
        value='Drag',
        description='Mode:',
        layout=widgets.Layout(width='200px')
    )

    mode_select.observe(update_mode, names='value')
    GUI = widgets.AppLayout(header=mode_select, 
                            left_sidebar=None, 
                            center=fig.canvas, 
                            right_sidebar=None, 
                            footer=None, pane_heights = [1, 30,0])
    # Initialize plot
    update_plot(x_min, x_max)
    fig.canvas.draw_idle()

    # Control box for displaying controls and plot
    return(GUI)

