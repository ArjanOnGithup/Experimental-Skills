[![Binder](https://binderhub.app.rug.nl/badge_logo.svg)](https://binderhub.app.rug.nl/v2/gh/ArjanOnGithup/Experimental-Skills/HEAD)

# spectHR - Cardiovascular Spectral Analysis Toolkit

`spectHR` is a Python library designed for interactive analysis of time series data, particularly focused on ECG and breathing patterns. The library provides tools for detecting peaks (R-tops) in ECG data, spectral analysis, and interactive visualization of time series data. It includes various modes for modifying, selecting, and analyzing R-tops and other key events in the data.

## Features

- **ECG and Breathing Pattern Analysis**: Process and analyze time series data, including ECG and breathing patterns.
- **Peak Detection (R-tops)**: Automatically detect R-top times in ECG signals.
- **Interactive Plotting**: Use draggable vertical lines to visualize and manipulate R-tops within a plot.
- **Zoom and Epoch Selection**: Interactively zoom into regions of interest and select epochs for marking.
- **Spectral Analysis**: Perform cardiovascular spectral analysis to study heart rate variability and other metrics.

## Installation

### Requirements

- Python 3.7+
- Jupyter notebook or JupyterLab
- ipywidgets
- Voilà (for interactive visualization)

### Install the library

You can install `spectHR` using pip:

```bash
pip install spectHR
```
Or, if you're developing locally, clone the repository and install it in editable mode:

```bash
Copy code
git clone https://github.com/yourusername/spectHR.git
cd spectHR
pip install -e .
```

## Usage
To use spectHR in your Jupyter notebook, import the necessary components and load your ECG data for analysis.

```python
import spectHR as cs

# Example: Load ECG data and perform peak detection
DataSet = cs.SpectHRDataset("Example Data/SUB_002.xdf") 
DataSet = cs.calcPeaks(DataSet)
```
Once the data is loaded, you can visualize it with interactive plots:

```python
GUI = cs.spectplot(DataSet)  # Plot ECG with draggable R-top lines
```

### Available Modes

Drag: Move the vertical lines (R-tops) along the x-axis to adjust detection.
Remove: Select and remove individual R-tops by clicking on the lines.
Add: Add a new R-top at a specific location on the plot.
Find: Identify peaks within a selected x-range.

This will allow you to interact with the ECG plot, dragging R-top lines and updating the dataset accordingly.

## Contributing
If you'd like to contribute to spectHR, feel free to fork the repository and submit pull requests. Please ensure that your code follows the existing style and includes appropriate tests.

## License
spectHR is released under the GNU License. See the LICENSE file for more details.

