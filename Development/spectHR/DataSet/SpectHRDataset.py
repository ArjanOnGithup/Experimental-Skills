import pandas as pd
import numpy as np
import pyxdf
import os
from pathlib import Path
import pickle

from datetime import datetime
from spectHR.Tools.Logger import logger
from spectHR.Tools.Webdav import copyWebdav

class TimeSeries:
    """
    A class to represent a time series with time and level data, along with optional sampling rate.

    Attributes:
        time (pd.Series): Timestamps of the time series.
        level (pd.Series): Values corresponding to each timestamp.
        srate (float): Sampling rate, calculated if not provided.

    Methods:
        slicetime(time_min, time_max):
            Returns a subset of the TimeSeries between specified time bounds.
        to_dataframe():
            Converts the TimeSeries to a Pandas DataFrame.
    """
    
    def __init__(self, x, y, srate=None):
        """
        Initializes the TimeSeries object.

        Args:
            x (iterable): Time values of the time series.
            y (iterable): Level values corresponding to each time value.
            srate (float, optional): Sampling rate. If not provided, it is calculated automatically.
        """
        self.time = pd.Series(x)
        self.level = pd.Series(y)

        # Automatically calculate sampling rate if not provided
        self.srate = srate if srate is not None else round(1.0 / self.time.diff().mean())

    def slicetime(self, time_min, time_max):
        """
        Returns a subset of the TimeSeries between specified time bounds.

        Args:
            time_min (float): Start of the time range.
            time_max (float): End of the time range.

        Returns:
            TimeSeries: A new TimeSeries object with data between the specified times.
        """
        mask = (self.time >= time_min) & (self.time <= time_max)
        return TimeSeries(self.time[mask], self.level[mask], self.srate)

    def to_dataframe(self):
        """
        Converts the TimeSeries to a Pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing time, level, and sampling rate.
        """
        return pd.DataFrame({"time": self.time, "level": self.level, "srate": [self.srate] * len(self.time)})


class SpectHRDataset:
    """
    A class to represent a dataset containing ECG, breathing, and event data.

    Attributes:
        ecg (TimeSeries): The ECG data as a TimeSeries object.
        br (TimeSeries): The breathing data as a TimeSeries object.
        events (pd.DataFrame): A DataFrame containing event timestamps and labels.
        history (list): A list of actions performed on the dataset.
        par (dict): Parameters associated with various actions.
        starttime (float): The start time of the dataset.

    Methods:
        loadData(filename, ecg_index=None, br_index=None, event_index=None):
            Loads data from an XDF file and initializes the dataset.
        log_action(action_name, params):
            Logs an action with its parameters into the dataset history.
    """
    def __init__(self, filename, ecg_index=None, br_index=None, event_index=None, par=None, reset = False, use_webdav = False):
        """
        Initializes the SpectHRDataset by loading data from a file.

        Args:
            filename (str): Path to the XDF file.
            ecg_index (int, optional): Index of the ECG stream in the XDF file. Defaults to None.
            br_index (int, optional): Index of the breathing stream in the XDF file. Defaults to None.
            event_index (int, optional): Index of the event stream in the XDF file. Defaults to None.
            par (dict, optional): Initial parameters for the dataset. Defaults to None.
        """
        
        
        self.ecg = None
        self.br = None
        self.bp = None
        self.events = None

        self.history = []
        self.par = par if par is not None else {}
        self.starttime = None

        self.datadir = os.path.dirname(filename)
        self.filename = os.path.basename(filename)
        self.pkl_filename = os.path.splitext(self.filename)[0] + ".pkl"
        self.pkl_path = os.path.join(self.datadir, self.pkl_filename)
        self.file_path = os.path.join(self.datadir, self.filename)

        if use_webdav:
            if not Path(self.file_path).exists():
                copyWebdav(self.file_path)

        # Load data from pickle if available; otherwise, process the XDF file
        if Path(self.pkl_path).exists() and not reset:
            logger.info(f"Loading dataset from pickle: {self.pkl_path}")
            self.load_from_pickle()
        elif Path(self.file_path).exists():
            logger.info(f"Loading dataset from XDF: {self.file_path}")
            self.loadData(self.file_path, ecg_index, br_index, event_index)
            self.save()
        else:
            logger.error(f"File {self.file_path} was not found")

    def save(self):
        """
        Saves the current state of the dataset as a pickle file.
        """
        try:
            with open(self.pkl_path, "wb") as pkl_file:
                pickle.dump(self, pkl_file)
            logger.info(f"Dataset saved as pickle: {self.pkl_path}")
        except Exception as e:
            logger.error(f"Failed to save pickle file: {e}")

    def load_from_pickle(self):
        """
        Loads the dataset from a pickle file.
        """
        try:
            with open(self.pkl_path, "rb") as pkl_file:
                data = pickle.load(pkl_file)
            self.__dict__.update(data.__dict__)
            logger.info("Dataset loaded successfully from pickle")
        except Exception as e:
            logger.error(f"Failed to load pickle file: {e}")
            
    def loadData(self, filename, ecg_index=None, br_index=None, bp_index=None, event_index=None):
        """
        Loads data from an XDF file into the dataset.

        Args:
            filename (str): Path to the XDF file.
            ecg_index (int, optional): Index of the ECG stream in the XDF file. Defaults to None.
            br_index (int, optional): Index of the breathing stream in the XDF file. Defaults to None.
            event_index (int, optional): Index of the event stream in the XDF file. Defaults to None.
        """
        rawdata, _ = pyxdf.load_xdf(filename)

        # Identify ECG stream automatically if not provided
        if ecg_index is None:
            ecg_index = next((i for i, d in enumerate(rawdata) if d['info']['name'][0].startswith('Polar')), None)
            if ecg_index is None:
                logger.info("There is no stream named 'Polar'")

        # Identify event stream automatically if not provided
        if event_index is None:
            event_index = next((i for i, d in enumerate(rawdata) if d['info']['name'][0].startswith('TaskMarkers')), None)
            if event_index is None:
                logger.info("There is no stream named 'TaskMarkers'")
                
        # Load ECG data
        if ecg_index is not None:
            ecg_timestamps = pd.Series(rawdata[ecg_index]["time_stamps"])
            self.starttime = ecg_timestamps[0]  # Set dataset start time
            
            ecg_levels = pd.Series(rawdata[ecg_index]["time_series"].flatten())
            ecg_timestamps -= self.starttime
            # pragmatic apprauch. Might do better. This flips the signal if it thinks it needs to...
            if abs(np.mean(ecg_levels) - np.min(ecg_levels)) > abs(np.mean(ecg_levels) - np.max(ecg_levels)): 
                logger.info('flipping the signal')
                ecg_levels = -ecg_levels
            self.ecg = TimeSeries(ecg_timestamps, ecg_levels)

        # Load breathing data
        if br_index is not None:
            logger.info("Expecting Breathing data")
            br_timestamps = pd.Series(rawdata[br_index]["time_stamps"])
            br_levels = pd.Series(rawdata[br_index]["time_series"].flatten())
            br_timestamps -= self.starttime
            
            self.br = TimeSeries(br_timestamps, br_levels)

        # Load bloodpressure data
        if bp_index is not None:
            logger.info("Expecting Bloodpressure data")
            bp_timestamps = pd.Series(rawdata[bp_index]["time_stamps"])
            bp_levels = pd.Series(rawdata[bp_index]["time_series"].flatten())
            bp_timestamps -= self.starttime
            
            self.bp = TimeSeries(bp_timestamps, bp_levels)

        # Load event data
        if event_index is not None:
            event_timestamps = pd.Series(rawdata[event_index]["time_stamps"])
            event_labels = pd.Series(rawdata[event_index]["time_series"])
            event_labels = event_labels.apply(lambda x: x[0])
            self.events = pd.DataFrame({
                'time': event_timestamps - self.starttime,
                'label': event_labels
            })
            self.create_epoch_series()

    def create_epoch_series(self):
        """
        Creates an 'epoch' series within the dataset to map each time point in the ECG
        to a corresponding epoch based on event labels ('start' and 'end').

        Returns:
            pd.Series: A series with epoch labels for each time index in the ECG and RTopTimes.
        """
        if self.events is None:
            logger.error('No events availeable for epoch generation')

        self.ecg_epoch = pd.Series(index=self.ecg.time.index, dtype="object")

        labels = self.events['label'].str.lower()
        start_indices = self.events[labels.str.startswith('start')].index
        end_indices = self.events[labels.str.startswith('end')].index

        # Create epoch identifiers
        epoch_id = None
        for start_idx in start_indices:
            epoch_name = self.events['label'][start_idx][5:].strip()  # Get the epoch name
            start_time = self.events['time'][start_idx]

            # Find the corresponding 'end' time
            if len(end_indices) > 0 and end_indices[0] > start_idx:
                end_time = self.events['time'][end_indices[0]]
            else:
                # Handle missing 'end', use next 'start' or end of data
                end_time = (
                    self.events['time'][start_indices[start_indices.get_loc(start_idx) + 1]]
                    if start_idx + 1 < len(start_indices)
                    else self.ecg.time.iloc[-1]
                )

            # Assign epoch label to the time series (ecg and RTopTimes)
            self.ecg_epoch.loc[(self.ecg.time >= start_time) & (self.ecg.time <= end_time)] = epoch_name
        
    def log_action(self, action_name, params):
        """
        Logs an action performed on the dataset.

        Args:
            action_name (str): Name of the action.
            params (dict): Parameters associated with the action.
        """
        self.history.append({
            'action': action_name,
            'timestamp': datetime.now(),
            'parameters': params
        })
