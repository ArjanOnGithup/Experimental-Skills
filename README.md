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
- pyhrv
- ipyvuetify (for nicer looking widgets)


### Install the library
<not yet. but you can clone this repo...>
 
You can install `spectHR` using pip:

```bash
pip install spectHR
```
Or, if you're developing locally, clone the repository and install it in editable mode:

```bash
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
This function systematically classifies Inter-Beat Intervals (IBIs) derived from R-top times in an ECG dataset based on statistical thresholds. Each classification captures specific temporal characteristics or patterns in the intervals between successive heartbeats:

1. "N" (Normal): IBIs that fall within the expected range, determined by a rolling average and a standard deviation envelope (lower and higher thresholds). These intervals represent the individual's typical cardiac rhythm, without deviations beyond defined statistical boundaries.


2. "S" (Short): An IBI is labeled as "Short" if it is significantly smaller than the lower threshold (lower). This classification highlights faster-than-usual intervals that deviate from the individual's baseline rhythm.


3. "L" (Long): IBIs exceeding the upper threshold (higher) are categorized as "Long." These represent slower-than-usual intervals, reflecting a departure from the individual's expected rhythm.


4. "TL" (Too Long): An IBI is marked as "Too Long" if it surpasses an absolute duration threshold (Tmax), signifying intervals that are exceptionally prolonged and may indicate abnormalities or measurement artifacts.


5. "SL" (Short-Long): This classification identifies a specific pattern where a "Short" IBI is immediately followed by a "Long" IBI. Such sequences may indicate variability in cardiac timing, often observed in transitional patterns or measurement noise.


6. "SNS" (Short-Normal-Short): This label applies to a sequence of three consecutive IBIs, where a "Short" IBI is followed by a "Normal" IBI, then another "Short" IBI. This pattern highlights irregularities interspersed with typical intervals.



The algorithm calculates a moving average and standard deviation of IBIs over a sliding time window (Tw), defining dynamic, individual-specific thresholds for classifying deviations. Each IBI is assessed against these thresholds and assigned an appropriate label. Subsequent steps ensure detection of sequential patterns like "SL" and "SNS," enhancing the granularity of the classification.

The function also provides a summary of detected classifications, logging the frequency of each label. This systematic approach helps identify deviations from regular heartbeat intervals and potential artifacts, supporting detailed analysis of ECG data.


Once the data is loaded, you can visualize it with interactive plots:

```python
GUI = cs.prepPlot(DataSet)  # Plot ECG with draggable R-top lines
```

### Available Modes

- Drag: Move the vertical lines (R-tops) along the x-axis to adjust detection.
- Remove: Select and remove individual R-tops by clicking on the lines.
- Add: Add a new R-top at a specific location on the plot.
- Find: Identify peaks within a selected x-range.

This will allow you to interact with the ECG plot, dragging R-top lines and updating the dataset accordingly.

## Contributing
If you'd like to contribute to spectHR, feel free to fork the repository and submit pull requests. Please ensure that your code follows the existing style and includes appropriate tests.

## License
spectHR is released under the GNU License. See the LICENSE file for more details.

