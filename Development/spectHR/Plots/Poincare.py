import matplotlib.pyplot as plt
import numpy as np
import mplcursors
import copy
from matplotlib.patches import Ellipse
from ipywidgets import HBox, VBox, Checkbox, Output, Layout
from spectHR.Tools.Params import *
from spectHR.Tools.Logger import logger

def poincare(dataset):
    # Make a deep copy of the DataFrame and filter out rows with NaN in the 'epoch' column
    df = copy.deepcopy(dataset.RTops).dropna(subset=['epoch'])

    # Validate the DataFrame
    required_columns = {'ibi', 'epoch', 'time'}
    if not all(col in df.columns for col in required_columns):
        raise ValueError(
            "DataFrame must contain at least two rows and columns 'ibi', 'epoch', and 'time'."
        )
    if df.shape[0] < 2:
        raise ValueError("The DataFrame must have at least two rows to create a Poincaré plot.")

    # Ensure 'epoch' column is a consistent type (e.g., string)
    df['epoch'] = df['epoch'].astype(str)
    
    # Extract x (current IBI), y (next IBI), epochs, and times
    x = df['ibi'][:-1].values
    y = df['ibi'][1:].values
    epochs = df['epoch'][:-1].values
    times = df['time'][:-1].values

    # Create the figure
    fig, ax = plt.subplots(figsize=(5, 5))
    scatter_handles = {}
    ellipse_handles = {}
    global_indices = {}
    unique_epochs = np.unique(epochs)
    # make sure there is an selection list
    if not hasattr(dataset, 'active_epochs'):
        dataset.active_epochs = {}
        for epoch in unique_epochs:
            dataset.active_epochs.update({epoch: True})
            
    for epoch in unique_epochs:
        visible = dataset.active_epochs[epoch]
        # Mask data for each unique epoch
        mask = epochs == epoch
        scatter = ax.scatter(x[mask], y[mask], label=f'{epoch}', alpha=0.4)
        scatter_handles[epoch] = scatter

        # Compute SD1 & SD2
        _sd1 = np.std(np.subtract(x[mask], y[mask]) / np.sqrt(2))
        _sd2 = np.std(np.add(x[mask], y[mask]) / np.sqrt(2))
        ibm = np.mean(x[mask])
        col = scatter.get_facecolor()
        ellipse = Ellipse(
            (ibm, ibm), _sd1 * 2, _sd2 * 2, angle=-45,
            linewidth=2, zorder=1, facecolor=col, edgecolor=col
        )
        ax.add_artist(ellipse)
        ellipse_handles[epoch] = ellipse
        scatter_handles[epoch].set_visible(visible)
        ellipse_handles[epoch].set_visible(visible)

        # Store the global indices of the points in this scatter
        global_indices[epoch] = np.where(mask)[0]

    # Add hover functionality with mplcursors
    cursor = mplcursors.cursor(list(scatter_handles.values()), highlight=True, hover=False)
    def on_hover(sel):
        # Get the global index of the selected point
        scatter_idx = list(scatter_handles.values()).index(sel.artist)
        epoch = list(scatter_handles.keys())[scatter_idx]
        global_idx = global_indices[epoch][sel.index]

        # Update the annotation with the correct global values
        sel.annotation.set_text(
            f"{epochs[global_idx]}\nTime: {round(times[global_idx], 2)}"
        )
    cursor.connect("add", on_hover)

    # Plot formatting
    ax.set_title('Poincaré Plot', fontsize=14)
    ax.set_xlabel('IBI (ms)', fontsize=12)
    ax.set_ylabel('Next IBI (ms)', fontsize=12)
    ax.axline((0, 0), slope=1, color='gray', linestyle='--', linewidth=0.7)
    #ax.legend(fontsize=5, title="Epochs")
    ax.grid(True)

    # Output widget for the plot
    plot_output = Output()
    with plot_output:
        plt.show()

    # Create checkboxes for each epoch
    # Define a layout with minimal spacing for the VBox containing the checkboxes
    vbox_layout = Layout(display='flex', flex_flow='column', align_items='flex-start', gap='0px')
    # Define a layout with no margin for individual checkboxes
    checkbox_layout = Layout(margin='0px', padding='0px',  height='20px')

    checkboxes = {}
    def update_visibility(change):
        epoch = change.owner.description
        visible = change.new
        scatter_handles[epoch].set_visible(visible)
        ellipse_handles[epoch].set_visible(visible)
        dataset.active_epochs[epoch] = visible

        with plot_output:
            fig.canvas.draw_idle()
    
    for epoch in unique_epochs:
        checkbox = Checkbox(value=dataset.active_epochs[epoch] , description=epoch,  layout=checkbox_layout)
        checkbox.observe(update_visibility, names='value')
        checkboxes[epoch] = checkbox

    # Create the HBox with the VBox for checkboxes and the plot output
    return HBox([VBox(list(checkboxes.values()), layout=vbox_layout), plot_output])

