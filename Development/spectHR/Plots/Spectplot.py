import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import FancyArrowPatch
#from matplotlib.text import Annotation
#import mplcursors
import ipywidgets as widgets
import math

from ..ui.LineHandler import LineHandler, AreaHandler
import numpy as np
import pandas as pd

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
    out = widgets.Output()
    display(out)

    RTopColors = {'N': 'green', 'L': 'cyan', 'S': 'magenta', 'T': 'orange', '1': 'turquoise', '2': 'lightseagreen'}    
    def update_plot(x_min, x_max):
        """
        Redraw the ECG plot, R-top times, and breathing rate (if available).
        This function also adjusts the plot properties for the selected x-axis limits.

        Parameters:
        - x_min (float): Minimum x-axis limit for the zoomed view.
        - x_max (float): Maximum x-axis limit for the zoomed view.
        """
        
        plot_ecg_signal(ax_ecg, data.ecg.time, data.ecg.level)

        # Plot R-top times if available in the data
        if hasattr(data.ecg, 'RTopTimes'):
            
            # Plot only R-tops within x_min and x_max
            visible_rtops = [(t, c) for t, c in sorted(zip(data.ecg.RTopTimes, data.ecg.classID))
                         if x_min <= t <= x_max]
            if visible_rtops:
                if len(visible_rtops) < 60:
                    plot_rtop_times(ax_ecg, visible_rtops, line_handler)  # Plot VLines in the current view

            ax_ecg.set_ylim(ax_ecg.get_ylim()[0], ax_ecg.get_ylim()[1] * 1.2)
            #data.ecg.ibi = np.append(np.diff(data.ecg.RTopTimes), 0)
            #plot_rtop_times(ax_ecg, zip(data.ecg.RTopTimes, data.ecg.classID, data.ecg.ibi), line_handler)
        
        set_ecg_plot_properties(ax_ecg, x_min, x_max)
        
        # Plot the breathing rate if available in the data
        if ax_br is not None and data.br is not None:
            plot_breathing_rate(ax_br, data.br.time, data.br.level, x_min, x_max, line_handler)

        fig.canvas.draw_idle()

    def on_press(event):
        """
        Handles the mouse press event on the overview plot to initiate dragging.
        Determines the area (left, right, or center) that is clicked for zoom adjustment.
        """
        nonlocal drag_mode, initial_xmin, initial_xmax
        if event.inaxes != ax_overview:  # If click is outside the overview plot
            return

        # Check if the press is within the draggable region (x_min, x_max)
        if x_min <= event.xdata <= x_max:
            initial_xmin, initial_xmax = x_min, x_max
            dist = x_max - x_min
            # Determine drag mode based on proximity to the edges of the zoom box
            if abs(event.xdata - x_min) < 0.3 * dist:
                drag_mode = 'left'
            elif abs(event.xdata - x_max) < 0.3 * dist:
                drag_mode = 'right'
            else:
                drag_mode = 'center'

    def on_drag(event):
        """
        Handles the dragging event for adjusting the zoom region based on the drag mode.
        Adjusts the x_min and x_max limits depending on where the mouse is dragged.
        """
        nonlocal x_min, x_max, drag_mode, initial_xmin, initial_xmax
        if drag_mode is None or event.inaxes != ax_overview:  # If not in drag mode or outside the overview plot
            return

        # Adjust the zoom limits based on drag mode (left, right, or center)
        if drag_mode == 'left':
            x_min = min(event.xdata, x_max - 0.1)
        elif drag_mode == 'right':
            x_max = max(event.xdata, x_min + 0.1)
        elif drag_mode == 'center':
            dx = event.xdata - 0.5 * (initial_xmin + initial_xmax)
            x_min = initial_xmin + dx
            x_max = initial_xmax + dx

        # Update the zoom box position
        positional_patch.set_x(x_min)
        positional_patch.set_width(x_max - x_min)
        fig.canvas.draw_idle()

    def on_release(event):
        """Resets the dragging mode upon mouse release."""
        nonlocal drag_mode
        drag_mode = None
        update_plot(x_min, x_max)
        fig.canvas.draw_idle()

    def update_mode(change):
        """Update the mode in LineHandler based on dropdown selection."""
        line_handler.update_mode(change['drag'])


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
        """
        Plots the ECG signal on an overview plot with a shaded rectangle indicating the zoom region.
        """
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

    def plot_rtop_times(ax, vis_rtops, line_handler):
        """
        Plots vertical lines and arrows for each R-top time with labels indicating the IBI value.
        """
        h = ax.get_ylim()[1] + (0.05 * (ax.get_ylim()[1] - ax.get_ylim()[0]))
        line_handler.draggable_lines = []
        line_handler.lines = []

        Rt = [num for num, _ in vis_rtops]
        ibis = np.append(np.diff(Rt), 0)
        RTOPS = zip(*zip(*vis_rtops), ibis)
        for rtop in tuple(RTOPS):
            line_handler.add_line(ax, rtop[0], color=RTopColors[rtop[1]])
            if rtop[2] != 0:
                #Draw a double-sided arrow from the current R-top to the next
                arrow = FancyArrowPatch((rtop[0], h), 
                                     (rtop[0]+rtop[2], h), 
                                    arrowstyle='<->', color='blue', mutation_scale=15, linewidth=.5)
                ax.add_patch(arrow)
    
                ax.text(
                    rtop[0]+(.5*rtop[2]), 
                    h,  # Offset above the plot
                    f"{1000*rtop[2]:.0f}", fontsize=6, rotation = 0,
                    horizontalalignment='center', verticalalignment='bottom', color='blue', bbox=dict(facecolor = ax.get_facecolor(), edgecolor = ax.get_facecolor(), alpha = .4)
                )

    def set_ecg_plot_properties(ax, x_min, x_max):
        """Configure ECG plot properties."""
        ldisp = int(math.log10(abs(data.ecg.level.max()-data.ecg.level.min())))
        tdisp = round(math.log10(x_max-x_min),0)
        
        ax.set_title('')
        ax.set_xlabel('Time (seconds)')
        #ax.set_ylabel('ECG Level (mV)')
        ax.set_xlim(x_min, x_max)
        
        ax.xaxis.set_major_locator(MultipleLocator(math.pow(10,tdisp-1)))  # Major ticks every 1 second
        ax.xaxis.set_minor_locator(MultipleLocator(math.pow(10,tdisp-1)/5))  # Minor ticks every 0.2 seconds
        #ax.xaxis.set_minor_locator(AutoMinorLocator())  # Minor ticks every 0.2 seconds

        ax.yaxis.set_major_locator(MultipleLocator(math.pow(10,ldisp))) 
        ax.yaxis.set_minor_locator(MultipleLocator(math.pow(10,ldisp)/5))

        ax.xaxis.grid(which='minor', color='salmon', lw=0.3)
        ax.xaxis.grid(which='major', color='r', lw=0.7)
        ax.yaxis.grid(which='minor', color='salmon', lw=0.3)
        ax.yaxis.grid(which='major', color='r', lw=0.7)
        
        ax.grid(True, 'major', alpha = .3)
        ax.grid(True, 'minor', alpha = .2)

    def plot_ecg_signal(ax, ecg_time, ecg_level):
        """Plot the ECG signal on the provided axis."""
        ax.clear()
        ax.plot(ecg_time, ecg_level, label='ECG Signal', color='blue', linewidth = .7, alpha = .8)

    def plot_breathing_rate(ax, br_time, br_level, x_min, x_max, line_handler):
        """Plot breathing rate data on a separate axis."""
        ax.clear()
        ax.plot(br_time, br_level, label='Breathing Signal', color='green')
        ax.set_ylabel('Breathing Level')
        ax.grid(True)

    def on_prev_clicked(button):
        # find the first RTopTime with a non-'N' label, smaller then x_min
        nonlocal x_min, x_max
        x_range = x_max - x_min
        idx = data.ecg.RTopTimes[(pd.Series(data.ecg.classID) == 'S') & (data.ecg.RTopTimes < (x_min -  (.51*x_range)))]
        next_idx = idx.iloc[0] if not idx.empty else None     
        
        if next_idx is not None:
            x_min = next_idx-(.5*x_range)
            x_max = x_min + x_range
 
        update_plot(x_min, x_max)
        positional_patch.set_x(x_min)
        positional_patch.set_width(x_max - x_min)
        fig.canvas.draw_idle()
    
    def on_nex_clicked(button):
        # find the first RTopTime with a non-'N' label, smaller then x_min
        nonlocal x_min, x_max            
        x_range = x_max - x_min
        idx = data.ecg.RTopTimes[(pd.Series(data.ecg.classID) == 'S') & (data.ecg.RTopTimes > (x_min + (.51*x_range)))]
        next_idx = idx.iloc[0] if not idx.empty else None     
        if next_idx is not None:
            x_min = next_idx-(.5*x_range)
            x_max = x_min + x_range

        positional_patch.set_x(x_min)
        positional_patch.set_width(x_max - x_min)                
        update_plot(x_min, x_max)
        fig.canvas.draw_idle()
 
    # Main Plot: Configure theme
    plt.ioff()
    plt.title('')
    
    # Initialize x-axis limits based on input or data
    x_min = x_min if x_min is not None else data.ecg.time.min()
    x_max = x_max if x_max is not None else data.ecg.time.max()

    # Create figure and axis handles
    fig, ax_ecg, ax_overview, ax_br = create_figure_axes(data)
    fig.set_figwidth(21) 
    fig.set_figheight(5) 
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

    update_plot(x_min, x_max)
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

    prev = widgets.Button(description="Previous")
    nex = widgets.Button(description="Next")
    
    prev.on_click(on_prev_clicked)
    nex.on_click(on_nex_clicked)
    
    anomaly = widgets.HBox([prev, nex])
    
    GUI = widgets.AppLayout(header=mode_select, 
                            left_sidebar=None, 
                            center=fig.canvas, 
                            right_sidebar=None, 
                            footer=anomaly, pane_heights = [1, 10, 1])
    # Initialize plot
    #update_plot(x_min, x_max)
    fig.canvas.draw_idle()

    # Control box for displaying controls and plot
    return(GUI)

