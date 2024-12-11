import matplotlib.pyplot as plt
import numpy as np
import mplcursors
import copy
from matplotlib.patches import Ellipse

def poincare(dataset):
    """
    Generates a Poincaré plot for the given dataset.

    A Poincaré plot is a scatter plot of consecutive inter-beat intervals (IBIs).
    The x-axis represents the current IBI, and the y-axis represents the next IBI.
    Points are color-coded by epoch, and hovering over a point reveals its epoch 
    and corresponding time.

    Parameters:
    -----------
    dataset : object
        An object containing a DataFrame `RTops` with the following columns:
        - 'ibi' (float): Inter-beat intervals (in milliseconds).
        - 'epoch' (str or int): Epoch labels.
        - 'time' (float): Time values associated with each IBI.

    Returns:
    --------
    None
        Displays an interactive scatter plot in a Matplotlib figure.
    """
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
    x = df['ibi'][:-1].values  # Current IBI
    y = df['ibi'][1:].values   # Next IBI
    epochs = df['epoch'][:-1].values  # Epoch labels (aligned with x)
    times = df['time'][:-1].values    # Time values (aligned with x)


    # Create the figure and scatter plot
    fig = plt.figure(figsize=(5, 5))
    unique_epochs = np.unique(epochs)
    scatter_handles = []
    global_indices = []

    for epoch in unique_epochs:
        # Mask data for each unique epoch
        mask = epochs == epoch
        scatter = plt.scatter(x[mask], y[mask], label=f'{epoch}', alpha = 0.3)
        scatter_handles.append(scatter)
        # Plot Ellises
        # SD1 & SD2 Computation: ref. pyhrv: poincare
        sd1 = np.std(np.subtract(x[mask], y[mask]) / np.sqrt(2))
        sd2 = np.std(np.add(x[mask], y[mask]) / np.sqrt(2))
        ibm = np.mean(x[mask])
        # Area of ellipse
        # carea = np.pi * sd1 * sd2
        # get the color from the scatter.
        col = scatter.get_facecolor()

        ellipse = Ellipse((ibm, ibm), sd1 * 2, sd2 * 2, angle = -45,linewidth = 2 ,zorder=1, facecolor = col, edgecolor = col, alpha = .1)
        fig.axes[0].add_artist(ellipse)
        # Store the global indices of the points in this scatter
        global_indices.append(np.where(mask)[0])

    # Add hover functionality with mplcursors
    cursor = mplcursors.cursor(scatter_handles, highlight=True, hover=False)

    def on_hover(sel):
        """
        Event handler for hover interactions. Updates the annotation text.

        Parameters:
        -----------
        sel : mplcursors.Selection
            The selected data point.
        """
        # Get the global index of the selected point
        scatter_idx = scatter_handles.index(sel.artist)
        global_idx = global_indices[scatter_idx][sel.index]

        # Update the annotation with the correct global values
        sel.annotation.set_text(
            f"Epoch: {epochs[global_idx]}\nTime: {round(times[global_idx], 2)}"
        )

    # Connect the hover callback to the cursor
    cursor.connect("add", on_hover)

    # Plot formatting
    plt.title('Poincaré Plot', fontsize=14)
    plt.xlabel('IBI (ms)', fontsize=12)
    plt.ylabel('Next IBI (ms)', fontsize=12)
    plt.axline((0, 0), slope=1, color='gray', linestyle='--', linewidth=0.7)
    plt.legend(fontsize=5, title="Epochs")
    plt.grid(True)

    # Display the plot
    plt.show()
