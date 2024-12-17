import matplotlib.pyplot as plt
import numpy as np
import mplcursors
import copy
from matplotlib.patches import Ellipse
from ipywidgets import HBox, VBox, Checkbox, Output, Layout
from spectHR.Tools.Params import *
from spectHR.Tools.Logger import logger

def poincare(dataset):
    """
    Generate an interactive Poincaré plot for a dataset containing Inter-Beat Intervals (IBI).

    This function plots the relationship between consecutive IBIs to form a Poincaré plot.
    It includes the following features:
      - Scatter points representing IBIs for specific epochs.
      - Ellipses to represent SD1 and SD2 measures of variability for each epoch.
      - Interactive visibility toggling for epochs using checkboxes.
      - Hover functionality to display epoch information and time of points.

    Args:
        dataset: An object with the following attributes:
            - RTops (pd.DataFrame): DataFrame containing IBI and epoch data.
                Required columns: 'ibi', 'epoch', 'time'.
            - unique_epochs (iterable): List or set of unique epoch labels.
            - active_epochs (dict, optional): A dictionary with epoch names as keys
                and booleans as values, indicating visibility of each epoch.

    Returns:
        ipywidgets.HBox: A widget containing the interactive Poincaré plot and checkboxes
            for toggling the visibility of epochs.

    Raises:
        ValueError: If required columns ('ibi', 'epoch', 'time') are missing or
            the DataFrame has fewer than two rows.
    """

    # Step 1: Preprocess the dataset
    # Create a deep copy of the RTops DataFrame to avoid modifying the original data
    df = copy.deepcopy(dataset.RTops).dropna(subset=['epoch'])  # Drop rows with missing 'epoch'

    # Validate the DataFrame structure
    required_columns = {'ibi', 'epoch', 'time'}
    if not all(col in df.columns for col in required_columns):
        raise ValueError("DataFrame must contain 'ibi', 'epoch', and 'time' columns.")
    if df.shape[0] < 2:
        raise ValueError("The DataFrame must have at least two rows for a Poincaré plot.")

    # Ensure that 'epoch' is of string type for consistency
    df['epoch'] = df['epoch'].astype(str)

    # Step 2: Prepare the data
    x = df['ibi'][:-1].values  # Current IBI (excluding the last row)
    y = df['ibi'][1:].values   # Next IBI (excluding the first row)
    epochs = df['epoch']       # Epoch column
    times = df['time'][:-1].values  # Time of current IBIs

    # Initialize the figure and axes for the plot
    fig, ax = plt.subplots(figsize=(7, 7))
    fig.canvas.toolbar_visible = False  # Hide the default Matplotlib toolbar

    # Dictionaries to store scatter, ellipse handles, and global indices for hover functionality
    scatter_handles = {}
    ellipse_handles = {}
    global_indices = {}

    # Retrieve unique epochs
    unique_epochs = dataset.unique_epochs

    # Ensure 'active_epochs' exists; initialize it if not present
    if not hasattr(dataset, 'active_epochs'):
        dataset.active_epochs = {epoch: True for epoch in unique_epochs}

    # Step 3: Plot scatter points and SD1/SD2 ellipses for each epoch
    for epoch in sorted(unique_epochs):
        visible = dataset.active_epochs[epoch]

        # Create a boolean mask for the current epoch
        mask = epochs.apply(lambda x: epoch in x)[:-1]  # Mask excludes the last row for consistency

        # Scatter plot for current epoch
        scatter = ax.scatter(x[mask], y[mask], label=epoch.title(), alpha=0.25)
        scatter_handles[epoch] = scatter

        # Compute SD1 and SD2 for the current epoch
        _sd1 = np.std(np.subtract(x[mask], y[mask]) / np.sqrt(2))  # Perpendicular to line of identity
        _sd2 = np.std(np.add(x[mask], y[mask]) / np.sqrt(2))       # Along the line of identity
        ibm = np.mean(x[mask])  # Mean IBI
        col = scatter.get_facecolor()  # Color of the scatter points

        # Create an ellipse to represent SD1 and SD2 variability
        ellipse = Ellipse(
            (ibm, ibm), _sd1 * 2, _sd2 * 2, angle=-45,
            linewidth=2, zorder=1, facecolor=col, edgecolor=col
        )
        ax.add_artist(ellipse)
        ellipse_handles[epoch] = ellipse

        # Set visibility based on 'active_epochs'
        scatter.set_visible(visible)
        ellipse.set_visible(visible)

        # Store the global indices of points for hover functionality
        global_indices[epoch] = np.where(mask)[0]

    # Step 4: Add hover functionality using mplcursors
    cursor = mplcursors.cursor(list(scatter_handles.values()), highlight=True, hover=False)
    
    def on_hover(sel):
        """
        Display epoch and time information on hover.

        Args:
            sel: The cursor selection event triggered by hovering.
        """
        scatter_idx = list(scatter_handles.values()).index(sel.artist)
        epoch = list(scatter_handles.keys())[scatter_idx]
        global_idx = global_indices[epoch][sel.index]

        # Update the annotation text with epoch and time information
        sel.annotation.set_text(f"{epochs[global_idx]}\nTime: {round(times[global_idx], 2)}")
    cursor.connect("add", on_hover)

    # Step 5: Plot formatting
    ax.set_title('Poincaré Plot', fontsize=14)
    ax.set_xlabel('IBI (ms)', fontsize=12)
    ax.set_ylabel('Next IBI (ms)', fontsize=12)
    ax.axline((0, 0), slope=1, color='gray', linestyle='--', linewidth=0.7)  # Line of identity
    # Filter scatter handles based on the dict_values
    scatters = [handle for label, handle in scatter_handles.items() if dataset.active_epochs[label]]

    ax.legend(handles = scatters, fontsize=5, title=None)

    ax.grid(True)

    # Step 6: Create output widget for the plot
    plot_output = Output()
    with plot_output:
        plt.show()

    # Step 7: Add checkboxes for toggling epoch visibility
    vbox_layout = Layout(display='flex', flex_flow='column', align_items='flex-start', gap='0px')
    checkbox_layout = Layout(margin='0px', padding='0px', height='20px')
    checkboxes = {}

    def update_visibility(change):
        """
        Update the visibility of scatter points and ellipses when a checkbox is toggled.

        Args:
            change: A dictionary containing the checkbox state change information.
        """
        epoch = change.owner.description
        visible = change.new
        scatter_handles[epoch].set_visible(visible)
        ellipse_handles[epoch].set_visible(visible)
        dataset.active_epochs[epoch] = visible

        with plot_output:
            fig.canvas.draw_idle()

    # Create a checkbox for each epoch
    for epoch in sorted(unique_epochs):
        checkbox = Checkbox(
            value=dataset.active_epochs[epoch],
            description=epoch,
            layout=checkbox_layout
        )
        checkbox.observe(update_visibility, names='value')
        checkboxes[epoch] = checkbox

    # Step 8: Return the interactive HBox layout with plot and checkboxes
    return HBox([plot_output, VBox(list(checkboxes.values())[::-1], layout=vbox_layout)])
