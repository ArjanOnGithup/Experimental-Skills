# Technical Manual for ECG Data Analysis Application

## Overview
This document provides an in-depth technical description of the ECG Data Analysis application. The application is designed to process and analyze ECG (electrocardiogram) data, identify R-top peaks, visualize data with interactive plots, and allow the user to manipulate vertical lines indicating R-top times. The app integrates with the `Shiny` framework for Python to provide an interactive web-based interface.

## Requirements

### Software Requirements
- Python 3.x
- Required Python libraries:
  - Shiny for Python
  - Matplotlib for plotting
  - Pandas for data manipulation
  - Numpy for numerical operations
  - ipywidgets for widget interactions in Jupyter
  - Plotly (if required for specific visualizations)
  - Other dependencies (refer to the full list in the `requirements.txt` file)

### Hardware Requirements
- A computer capable of running Python and JupyterLab
- A web browser for accessing the Shiny app interface

## Application Structure

### Main Components
The application is divided into the following primary components:
1. **ECG Data Handling**: 
   - The core class for handling ECG data is the `CarspanDataSet` class, which encapsulates the raw ECG data, metadata, and analysis results.
   - It includes methods for importing ECG data, filtering, detecting peaks, and updating the data based on user interactions.
   
2. **ECG Plotting**:
   - The ECG data is visualized using Matplotlib (and optionally Plotly). Interactive features include draggable vertical lines (for marking R-top peaks), zooming on the x-axis, and real-time updates when vertical lines are moved.
   - The `LineHandler` class is used to manage vertical lines, including adding, removing, and dragging lines.
   - The `RTopTimes` feature stores the positions of R-top peaks and updates these times as the lines are dragged.

3. **User Interaction**:
   - The user can select different modes (e.g., "add", "remove", "drag") for the vertical lines.
   - A dropdown menu is provided for selecting the current mode of interaction with the plot.

### Key Functions and Classes

#### `CarspanDataSet`
- Stores the ECG data, metadata, and parameters.
- Includes methods for importing data, applying preprocessing steps, and detecting peaks.

#### `LineHandler`
- Handles the plotting and interaction with draggable vertical lines.
- Manages zoom functionality on the x-axis and ensures that vertical lines are only plotted within the visible area.
- Allows for real-time updates of `RTopTimes` and IBI values when lines are dragged.

#### `plot_rtop_times()`
- Plots the ECG data with vertical lines indicating R-top times.
- Each R-top line is draggable, and the inter-beat interval (IBI) is displayed as a label above each line.

### Modes of Interaction
1. **Add Mode**: Users can click to add new vertical lines at specified x-axis positions.
2. **Remove Mode**: Users can click on existing vertical lines to remove them.
3. **Drag Mode**: Users can click and drag existing vertical lines, with the position being updated in real-time.

### Key Variables
- **`data.ecg.time`**: The time series data for the ECG signal.
- **`data.ecg.level`**: The actual ECG signal levels.
- **`data.ecg.RTopTimes`**: A list of timestamps for the R-top peaks.
- **`IBI`**: Inter-beat intervals calculated as the difference between consecutive R-top times.

## User Guide

### Running the Application
1. **Install Dependencies**:
   Ensure you have all the necessary Python libraries installed by running the following: