import numpy as np
import pandas as pd
import copy
import scipy.signal as signal
from spectHR.Tools.Logger import logger, handler

def calcPeaks(DataSet, par=None):
    """
    Detects R-tops (peaks) in an ECG signal and calculates the Inter-Beat Interval (IBI).

    Args:
        DataSet (CarspanDataSet): The dataset object containing ECG data.
        par (dict): Parameter dictionary for peak detection and filtering.

    Returns:
        DataSet (CarspanDataSet): The dataset with updated RTopTimes.
        par (dict): The parameter dictionary, updated if necessary.
    """
    
    default_par = {
        'MinPeakDistance': 300,  # ms
        'fSample': 130,          # Sampling frequency (Hz)
        'MinPeakHeight': None,    # This will be computed during calcPeaks
        'Classify': True
    }

    # Merge passed par with default if any
    if par is None:
        par = default_par
    else:
        par = {**default_par, **par}
    
    DS = copy.deepcopy(DataSet)

    # Store the final par used in the DataSet
    DS.par['calcPeaks'] = par

    # Step 1: Estimate a minimum peak height based on the median and standard deviation of the signal
    # This avoids detecting small noise fluctuations as peaks.
    par['MinPeakHeight'] = np.nanmedian(DS.ecg.level) + (1.5 * np.nanstd(DS.ecg.level))

    # Step 2: Convert MinPeakDistance from milliseconds to samples using the sampling frequency
    MinPeakDistance = ((par['MinPeakDistance'] / 1000) * par['fSample'])

    # Step 3: Detect peaks in the ECG signal using scipy's find_peaks method
    # 'height' specifies the minimum peak height, and 'distance' ensures peaks are spaced apart
    locs, props = signal.find_peaks(DS.ecg.level, height=par['MinPeakHeight'], distance=MinPeakDistance)
    
    # Step 4: Store the values of the ECG signal at the detected peak locations
    vals = DS.ecg.level.iloc[locs].array
    pre  = DS.ecg.level.iloc[locs-1].array
    post = DS.ecg.level.iloc[locs+1].array
    # Step 5: Calculate the rate of change (rc) before and after each peak
    # This gives insight into the sharpness of the peak (the difference between the peak and neighboring points)
    rc_before = np.abs(vals - pre)  # Difference with previous point
    rc_after = np.abs(post - vals)   # Difference with next point
    rc = np.maximum(rc_before, rc_after)  # Take the maximum of the two rates of change

    # Step 6: Optionally apply corrections to the peak times (uncomment if needed)
    correction = (post - pre) / par['fSample'] / 2.0 / np.abs(rc)
    
    # Print the number of detected R-tops for logging purposes
    logger.info(f"Found {len(locs)} r-tops")

    # Step 7: Update the dataset's RTopTimes with the time stamps corresponding to the detected peaks
    DS.ecg.RTopTimes = DS.ecg.time.iloc[locs] + correction
    DS.ecg.RTopTimes = DS.ecg.RTopTimes.reset_index(drop=True)

    DS.ecg.ibi = np.diff(DS.ecg.RTopTimes)
    # Log the action
    DS.log_action('calcPeaks', par)
    # Step 8: If warrented: classify and label the peaks 
    if par['Classify']:
        classify(DS)
    # Step 9: Return the updated dataset and the parameters
    return DS


def filterECGData(DataSet, par=None):
    """
    Placeholder function for filtering ECG data, which can be customized.
    Possible filtering techniques could include low-pass or band-pass filters 
    to clean the ECG signal.

    Args:
        DataSet (CarspanDataSet): The dataset object containing ECG data.
        par (dict): Parameter dictionary for filtering configurations.

    Returns:
        DataSet (CarspanDataSet): The filtered dataset (when implemented).
    """
    # Example filtering logic could go here
    # You could apply a band-pass filter using scipy or another library

    # Step 1: Choose filter parameters (this is just a placeholder for now)
    # e.g., highpass = 0.5, lowpass = 45.0, order = 4
       # Use default parameters if par is None
    default_par = {
        'channel': 'ecg',
        'filterType': 'highpass',  # Example: filter type (lowpass, highpass)
        'cutoff': 3,               # Hz: Cutoff frequency for the filter
        'order': 8,               # Filter order
        'fSample': DataSet.ecg.srate            # Sampling frequency (Hz)
    }

    # Merge passed par with default if any
    if par is None:
        par = default_par
    else:
        par = {**default_par, **par}

    # Create a deep copy of the DataSet to avoid modifying the original object
    DS = copy.deepcopy(DataSet)
    
    # Store the final par used in the DataSet
    DS.par['filterData'] = par

    # Apply the filter using SciPy's signal package
    nyquist = 0.5 * par['fSample']
    normal_cutoff = par['cutoff'] / nyquist

    # Example: lowpass or highpass filter
    if par['filterType'] == 'lowpass':
        b, a = signal.butter(par['order'], normal_cutoff, btype='low', analog=False)
    elif par['filterType'] == 'highpass':
        b, a = signal.butter(par['order'], normal_cutoff, btype='high', analog=False)

    channel = par['channel']
    # Apply the filter to the signal
    if channel == 'ecg':
        DS.ecg.y = pd.Series(signal.filtfilt(b, a, DS.ecg.level))
    if channel == 'bp':
        DS.bp.y = pd.Series(signal.filtfilt(b, a, DS.bp.level))
        
    # Log the action
    DS.log_action('filterData', par)

    logger.info(f"Data filtered with a {par['filterType']} filter (cutoff = {par['cutoff']} Hz).")
    return DS

import copy

def borderData(DataSet, par=None):
    """
    Creates a modified version of the provided DataSet by slicing TimeSeries based on the first and last events.

    Args:
        DataSet: The original dataset to be modified.
        par (dict, optional): Parameters for additional configurations. Defaults to None.

    Returns:
        CarspanDataSet: A new instance of CarspanDataSet with TimeSeries sliced.
    """
    default_par = {
        # Define any default parameters if needed
    }

    # Merge passed par with default if any
    if par is None:
        par = default_par
    else:
        par = {**default_par, **par}

    # Create a deep copy of the DataSet to avoid modifying the original object
    DS = copy.deepcopy(DataSet)
    # Ensure that events exist in the dataset
    if DS.events is not None and not DS.events.empty:
        # Get the first and last event timestamps
        first_event_time = DS.events['timestamp'].iloc[0]-1
        last_event_time = DS.events['timestamp'].iloc[-1]+1
        logger.info(f'Slicing from {first_event_time} to {last_event_time}')
        # Slice TimeSeries based on the first and last event times
        if DS.ecg is not None:
            DS.ecg = DS.ecg.slicetime(first_event_time, last_event_time)

        if DS.br is not None:
            DS.br = DS.br.slicetime(first_event_time, last_event_time)
        
    return DS
    

def classify(DataSet, par=None):
    """Performs the classification of IBIs based on the input R-top times.
    Classifies Inter-Beat Intervals (IBIs) based on statistical thresholds.

    Args:
        DataSet: The dataset containing the ECG data and R-top times.
        par (dict, optional): Parameters for classification.

    Returns:
        classID (list): Classification of IBIs ('N', 'L', 'S', 'T', '1', '2').
    """
    default_par = {"Tw": 51, "Nsd": 4, "Tmax": 5}

    if par is None:
        par = default_par
    else:
        par = {**default_par, **par}

    IBI = DataSet.ecg.ibi 
    classID = ['N'] * (len(IBI) + 1)  # Default to 'N'

    # Calculate moving average and standard deviation
    avIBIr = pd.Series(IBI).rolling(window=par["Tw"]).mean().to_numpy()
    SDavIBIr = pd.Series(IBI).rolling(window=par["Tw"]).std().to_numpy()

    lower = avIBIr - (par["Nsd"] * SDavIBIr)
    higher = avIBIr + (par["Nsd"] * SDavIBIr)

    # Classifications based on thresholds
    for i in range(len(IBI)):
        if IBI[i] > higher[i]:
            classID[i] = "L"  # Long IBI
        elif IBI[i] < lower[i]:
            classID[i] = "S"  # Short IBI
        elif IBI[i] > par["Tmax"]:
            classID[i] = "T"  # Too Long

    # Short followed by long
    for i in range(len(classID) - 1):
        if classID[i] == "S" and classID[i + 1] == "L":
            classID[i] = "1"  # Short-long sequence
        if i < len(classID) - 2:
            if classID[i] == "S" and classID[i + 1] == "N" and classID[i + 2] == "S":
                classID[i] = "2"  # Short-normal-short sequence

    # Assign the classID back to DataSet
    DataSet.ecg.classID = classID

    # Display classification counts
    unique_ids = set(classID)
    for id in unique_ids:
        count = classID.count(id)
        logger.info(f"Found {count} {id} rtops")

    return DataSet.ecg.classID
