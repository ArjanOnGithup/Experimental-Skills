import matplotlib.pyplot as plt
import numpy as np
import copy
from spectHR.Tools.Logger import logger

def gantt(dataset, labels = False):
    RTops = copy.deepcopy(dataset.RTops)  
    # Filter data: Keep rows containing at least one visible epoch
    if hasattr(dataset, 'active_epochs') and isinstance(dataset.active_epochs, dict):
        # If active_epochs exists, use it for filtering
        visible_epochs = {epoch: visible for epoch, visible in dataset.active_epochs.items() if visible}
    else:
        # If active_epochs does not exist, show all epochs
        visible_epochs = {epoch: True for epoch in dataset.unique_epochs}
    
    logger.info(f'visible_epochs')
    
    RTops["filtered_epoch"] = RTops["epoch"].apply(lambda x: [e for e in x if e in visible_epochs])
    RTops = RTops[RTops["filtered_epoch"].str.len() > 0]

    # Flatten epochs for plotting
    exploded = RTops.explode("filtered_epoch")
    # Get start and end times for each epoch
    epochs_gantt = (
        exploded.groupby("filtered_epoch")
        .agg(start=("time", "min"), end=("time", "max"))
        .reset_index()
    )
    # Sort epochs by start time
    epochs_gantt = epochs_gantt.sort_values(by="start", ascending=False).reset_index(drop=True)

    # Extract relevant data for the plot
    epoch_names = epochs_gantt["filtered_epoch"]
    start_times = epochs_gantt["start"]
    durations = epochs_gantt["end"] - epochs_gantt["start"]

    # Assign unique colors to each epoch
    colors = plt.cm.tab20(np.linspace(0, 1, len(epoch_names)))  # Use a colormap for unique colors
    color_dict = dict(zip(epoch_names, colors))  # Map epoch names to colors

    # Plot the Gantt chart
    fig, ax = plt.subplots(figsize=(15, 5))
    
    # Create horizontal bars with custom colors
    for i, epoch in enumerate(epoch_names):
        ax.barh(
            epoch, 
            durations[i], 
            left=start_times[i], 
            color=color_dict[epoch], 
            edgecolor="black", 
            alpha = .5
        )
    # Set y-ticks and labels with title case
    ax.set_yticks(range(len(epoch_names)))
    ax.set_yticklabels([name.title() for name in epoch_names])  # Convert labels to title case

    # Add labels and grid
    ax.set_xlabel("Time")
    ax.set_ylabel("")
    ax.set_title("")
    ax.grid(axis="y", linestyle="-", alpha=0.7)
    
    # Annotate start and end times on each bar
    if labels:
        for i, row in epochs_gantt.iterrows():
            ax.text(row["start"], i, f"{round(row['start'])}", va="center", ha="right", fontsize=8)
            ax.text(row["end"], i, f"{round(row['end'])}", va="center", ha="left", fontsize=8)
    
    # Show the plot
    plt.tight_layout()
    return fig