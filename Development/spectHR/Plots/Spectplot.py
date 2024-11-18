import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import FancyArrowPatch
import matplotlib

import ipywidgets as widgets
import math
import pdb

from ..ui.LineHandler import LineHandler, AreaHandler
import numpy as np
import pandas as pd
import logging

'''
from IPython.display import display, HTML
# Ensure responsive output container for the Jupyter cell
display(HTML("""
<style>
.jp-OutputArea-output {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    flex-grow: 1;
}
.widget-app-layout .app-layout-center {
    width: 100% !important;
    flex-grow: 1;
}
</style>
"""))
'''
logging.basicConfig(level = logging.INFO)

def spectplot(data, x_min = None, x_max = None):
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
                         if (x_min-1) <= t <= (x_max+1)]
            if visible_rtops:
                if len(visible_rtops) < 100:
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
        if event.inaxes == ax_overview:  # If click is on the overview plot
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
        elif event.inaxes == ax_ecg:
            if edit_mode == 'Add':
                line_handler.add_line(ax_ecg, event.xdata, 'red')
                data.ecg.RTopTimes.add(event.xdata)
                data.ecg.classID.append('N')
                fig.canvas.draw_idle()
                drag_mode = None

    def on_drag(event):
        """
        Handles the dragging event for adjusting the zoom region based on the drag mode.
        Adjusts the x_min and x_max limits depending on where the mouse is dragged.
        """
        nonlocal x_min, x_max, drag_mode, initial_xmin, initial_xmax
        if drag_mode is not None: 
            if event.inaxes == ax_overview:  # If click is on the overview plot
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
        """
        Resets the dragging mode upon mouse release.
        """
        nonlocal drag_mode        
        drag_mode = None
        update_plot(x_min, x_max)
        fig.canvas.draw_idle()

    def update_mode(change):
        """
        Update the mode in LineHandler based on dropdown selection.
        """   
        line_handler.update_mode(change['new'])
        edit_mode = change['new']

        # Helper to get figure dimensions in inches
    def calculate_figsize():
        dpi = matplotlib.rcParams['figure.dpi']  # Get the current DPI setting
        # Assume an approximate available width in pixels
        available_width = 2048  # Adjust this to test with different screen sizes
        width_in_inches = available_width / dpi
        height_in_inches = 6  # Choose an appropriate height
        return (width_in_inches, height_in_inches)

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
        figsize = calculate_figsize()
        if data.br is not None:
            fig, (ax_ecg, ax_overview, ax_br) = plt.subplots(
                3, 1, figsize = figsize, sharex = True,
                gridspec_kw = {'height_ratios': [4, 1, 3]}
            )
        else:
            fig, (ax_ecg, ax_overview) = plt.subplots(
                2, 1, figsize=figsize, sharex = False,
                gridspec_kw = {'height_ratios': [4, 1]}
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
                                  color = 'blue', alpha = 0.2, animated = False)

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
        #line_handler.draggable_lines = []
        #line_handler = LineHandler(fig, ax_ecg, callback_drag=update_rtop_times)
        Rt = [num for num, _ in vis_rtops]
        ibis = np.append(np.diff(Rt), 0)
        RTOPS = zip(*zip(*vis_rtops), ibis)
        for rtop in tuple(RTOPS):
            line_handler.add_line(ax, rtop[0], color = RTopColors[rtop[1]])
            if rtop[2] != 0:
                #Draw a double-sided arrow from the current R-top to the next
                arrow = FancyArrowPatch((rtop[0], h), 
                                        (rtop[0] + rtop[2], h), 
                                        arrowstyle = '<->', 
                                        color = 'blue', 
                                        mutation_scale = 15, 
                                        linewidth = .5)
                ax.add_patch(arrow)
    
                ax.text(
                    rtop[0] + (.5 * rtop[2]), 
                    h,  # Offset above the plot
                    f"{1000 * rtop[2]:.0f}", fontsize = 6, rotation = 0,
                    horizontalalignment = 'center', 
                    verticalalignment = 'bottom', 
                    color = 'blue', 
                    bbox = dict(facecolor = ax.get_facecolor(), 
                                edgecolor = ax.get_facecolor(), 
                                alpha = .4)
                )

    def set_ecg_plot_properties(ax, x_min, x_max):
        """
        Configure ECG plot properties.
        """
        ldisp = int(math.log10(abs(data.ecg.level.max() - data.ecg.level.min())))
        tdisp = round(math.log10(x_max - x_min), 0)
        
        ax.set_title('')
        ax.set_xlabel('Time (seconds)')
        #ax.set_ylabel('ECG Level (mV)')
        ax.set_xlim(x_min, x_max)
        
        ax.xaxis.set_major_locator(MultipleLocator(math.pow(10, tdisp - 1)))  # Major ticks every 1 second
        ax.xaxis.set_minor_locator(MultipleLocator(math.pow(10, tdisp - 1) / 5))  # Minor ticks every 0.2 seconds
        #ax.xaxis.set_minor_locator(AutoMinorLocator())  # Minor ticks every 0.2 seconds

        ax.yaxis.set_major_locator(MultipleLocator(math.pow(10, ldisp))) 
        ax.yaxis.set_minor_locator(MultipleLocator(math.pow(10, ldisp) / 5))
        # Remove y-axis ticks but keep the grid
        ax.set_yticks([])
        ax.xaxis.grid(which = 'minor', color = 'salmon', lw = 0.3)
        ax.xaxis.grid(which = 'major', color = 'r', lw = 0.7)
        ax.yaxis.grid(which = 'minor', color = 'salmon', lw = 0.3)
        ax.yaxis.grid(which = 'major', color = 'r', lw = 0.7)
        
        ax.grid(True, 'major', alpha = .3)
        ax.grid(True, 'minor', alpha = .2)

    def plot_ecg_signal(ax, ecg_time, ecg_level):
        """
        Plot the ECG signal on the provided axis.
        """
        ax.clear()
        ax.plot(ecg_time, ecg_level, label = 'ECG Signal', color = 'blue', linewidth = .7, alpha = .8)

    def plot_breathing_rate(ax, br_time, br_level, x_min, x_max, line_handler):
        """
        Plot breathing rate data on a separate axis.
        """
        ax.clear()
        ax.plot(br_time, br_level, label='Breathing Signal', color='green')
        ax.set_ylabel('Breathing Level')
        ax.grid(True)
        
    # Callback navigational functions.
    def update_view():
        """
        Updates the plot view by replotting data and adjusting the positional patch.
        """
        nonlocal x_min, x_max
        update_plot(x_min, x_max)
        positional_patch.set_x(x_min)
        positional_patch.set_width(x_max - x_min)
        fig.canvas.draw_idle()
        
    def on_begin_clicked(button):
        """
        Moves the view to the start of the dataset.
        """
        nonlocal x_min, x_max
        x_range = x_max - x_min
        x_min = data.ecg.time.iat[0]
        x_max = x_min + x_range
        update_view()
        
    def on_left_clicked(button):
        """
        Moves the view one range-width to the left.
        """
        nonlocal x_min, x_max
        x_range = x_max - x_min
        x_min = max(data.ecg.time.iat[0], x_min - x_range)
        x_max = x_min + x_range
        update_view()
        
    def on_prev_clicked(button):
        """
        Moves the view to center on the previous R-top with a specific label.
        """
        nonlocal x_min, x_max
        x_range = x_max - x_min
        idx = data.ecg.RTopTimes[
            (pd.Series(data.ecg.classID) == 'S') & (data.ecg.RTopTimes < x_min)
        ]
        next_idx = idx.iloc[-1] if not idx.empty else None
        if next_idx is not None:
            x_min = next_idx - (0.5 * x_range)
            x_max = x_min + x_range
        update_view()
        
    def on_wider_clicked(button):
        """
        Increases the view width by 1.5 times.
        """
        nonlocal x_min, x_max
        x_range = (x_max - x_min) / 1.5
        middle = (x_max + x_min) / 2
        x_min = max(middle - x_range, data.ecg.time.iat[0])
        x_max = min(x_min + (2 * x_range), data.ecg.time.iat[-1])
        update_view()
        
    def on_zoom_clicked(button):
        """
        Decreases the view width by 1/3 for zooming in.
        """
        nonlocal x_min, x_max
        x_range = (x_max - x_min) / 3
        middle = (x_max + x_min) / 2
        x_min = middle - x_range
        x_max = middle + x_range
        update_view()
        
    def on_nex_clicked(button):
        """
        Moves the view to center on the next R-top with a specific label.
        """
        nonlocal x_min, x_max
        x_range = x_max - x_min
        idx = data.ecg.RTopTimes[
            (pd.Series(data.ecg.classID) != 'N') & (data.ecg.RTopTimes > x_max)
        ]
        next_idx = idx.iloc[0] if not idx.empty else None
        if next_idx is not None:
            x_min = next_idx - (0.5 * x_range)
            x_max = x_min + x_range
        update_view()
        
    def on_right_clicked(button):
        """
        Moves the view one range-width to the right.
        """
        nonlocal x_min, x_max
        x_range = x_max - x_min
        x_min = min(data.ecg.time.iat[-1] - x_range, x_min + x_range)
        x_max = x_min + x_range
        update_view()
        
    def on_end_clicked(button):
        """
        Moves the view to the end of the dataset.
        """
        nonlocal x_min, x_max
        x_range = x_max - x_min
        x_max = data.ecg.time.iat[-1]
        x_min = x_max - x_range
        update_view()
    
    # Main Plot: Configure theme
    plt.ioff()
    plt.title('')
    
    # Initialize x-axis limits based on input or data
    x_min = x_min if x_min is not None else data.ecg.time.min()
    x_max = x_max if x_max is not None else data.ecg.time.max()

    # Create figure and axis handles
    fig, ax_ecg, ax_overview, ax_br = create_figure_axes(data)
    
    fig.canvas.toolbar_visible = False
    fig.canvas.header_visible = False
    fig.tight_layout()
    
    # Callback to update R-top times upon dragging a line
    def update_rtop_times(line, new_x):
        '''
        Update the position of an R-top time after dragging.
    
        This function updates the 'RTopTimes' series by replacing the closest 
        value to the original R-top time (line.origID) with a new value (new_x).
        It then reorders the 'RTopTimes' series and the 'classID' list based on 
        the updated R-top times, ensuring that the 'classID' entries correspond 
        correctly to their new R-top times.
    
        Args:
            line (object): The line object that represents the draggable R-top, 
                           containing the original R-top time (origID) and other 
                           properties.
            new_x (float): The new R-top time to update at the closest index to 
                           the original R-top time (line.origID).
        '''
        # Find the index of the R-top time closest to the original position
        closest_idx = (data.ecg.RTopTimes - line.origID).abs().idxmin()
        
        # Retrieve the value of the closest R-top time for logging purposes
        closest_value = data.ecg.RTopTimes.loc[closest_idx]
                
        # Update the R-top time at the closest index with the new value
        data.ecg.RTopTimes.loc[closest_idx] = new_x
        
        # Sort the R-top times in ascending order and reset the index
        sorted_indices = data.ecg.RTopTimes.argsort()
        data.ecg.RTopTimes = data.ecg.RTopTimes[sorted_indices]
        
        # Reorder the 'classID' list to match the new order of RTopTimes
        classID = pd.Series(data.ecg.classID)
        data.ecg.classID = classID[sorted_indices].tolist()
        
    line_handler = LineHandler(fig, ax_ecg, callback_drag=update_rtop_times)
    #area_handler = AreaHandler(fig, ax_ecg)    
    positional_patch  = plot_overview(ax_overview, data.ecg.time, data.ecg.level,  x_min, x_max)

    # State variables for dragging
    drag_mode = None
    initial_xmin, initial_xmax = x_min, x_max

    update_plot(x_min, x_max)
    # Connect the patch dragging events

    bpe = fig.canvas.mpl_connect('button_press_event', on_press)
    bod = fig.canvas.mpl_connect('motion_notify_event', on_drag)
    bor = fig.canvas.mpl_connect('button_release_event', on_release)

    # Mode selection dropdown widget for interaction
    mode_select = widgets.Dropdown(
        options = ['Drag', 'Add', 'Find', 'Remove'],
        value = 'Drag',
        description = 'Mode:',
        layout=widgets.Layout(width = '200px')
    )
    
    edit_mode = 'Drag'
    mode_select.observe(update_mode, names = 'value')
    figure_title = widgets.HTML(value='<center><H2>ECG signal</H2></center>', layout=widgets.Layout(width = '100%', justify_content = 'center'))
    spacer = widgets.Label(value='', layout=widgets.Layout(width = '200px'))
    header = widgets.HBox([mode_select, figure_title, spacer ], layout=widgets.Layout(justify_content = 'center', width = '100%'))
    '''
    Create navigation Buttons. These are used to navigate through the dataset
    '''
    begin = widgets.Button(icon = 'chevron-left')
    left = widgets.Button(icon = 'arrow-left')
    prev = widgets.Button(icon = "step-backward")
    wider = widgets.Button(icon = 'search-minus')    
    zoom = widgets.Button(icon = 'search-plus')    
    nex = widgets.Button(icon = "step-forward")
    right = widgets.Button(icon = 'arrow-right')
    end = widgets.Button(icon = 'chevron-right')

    '''
    Add the callbacks to the buttons.
    '''
    begin.on_click(on_begin_clicked)
    left.on_click(on_left_clicked)
    prev.on_click(on_prev_clicked)
    wider.on_click(on_wider_clicked)
    zoom.on_click(on_zoom_clicked)
    nex.on_click(on_nex_clicked)
    right.on_click(on_right_clicked)
    end.on_click(on_end_clicked)

    '''
    Create the navigation HBox
    '''
    navigator = widgets.HBox([begin, left, prev, zoom, wider, nex, right, end],
                    layout=widgets.Layout(justify_content = 'center', width = '100%'))

    '''
    Embed the Matplotlib figure in the AppLayout
    Create the GUI
    '''
    GUI = widgets.AppLayout(header = header, 
                            left_sidebar = None, 
                            center = widgets.Output(), 
                            right_sidebar = None, 
                            footer  = navigator, 
                            pane_heights = [1,10,1])
    with GUI.center:
        display(fig.canvas)

    fig.canvas.draw_idle()

    # Control box for displaying controls and plot
    return(GUI)

