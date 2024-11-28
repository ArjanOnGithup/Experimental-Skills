import pandas as pd
import numpy as np
import pyxdf
from datetime import datetime
from spectHR.Tools.Logger import logger, handler

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
    
    def __init__(self, filename, ecg_index=None, br_index=None, event_index=None, par=None):
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
        self.RTopTimes = None
        self.events = None

        self.history = []
        self.par = par if par is not None else {}
        self.starttime = None
        logger.info(f'Loading "{filename}"')

        self.loadData(filename, ecg_index, br_index, event_index)

    def loadData(self, filename, ecg_index=None, br_index=None, event_index=None):
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

        # Identify event stream automatically if not provided
        if event_index is None:
            event_index = next((i for i, d in enumerate(rawdata) if d['info']['name'][0].startswith('TaskMarkers')), None)

        # Load ECG data
        if ecg_index is not None:
            ecg_timestamps = pd.Series(rawdata[ecg_index]["time_stamps"])
            self.starttime = ecg_timestamps[0]  # Set dataset start time
            
            ecg_levels = pd.Series(rawdata[ecg_index]["time_series"].flatten())
            ecg_timestamps -= self.starttime
            
            self.ecg = TimeSeries(ecg_timestamps, ecg_levels)

        # Load breathing data
        if br_index is not None:
            br_timestamps = pd.Series(rawdata[br_index]["time_stamps"])
            br_levels = pd.Series(rawdata[br_index]["time_series"].flatten())
            br_timestamps -= self.starttime
            
            self.br = TimeSeries(br_timestamps, br_levels)

        # Load event data
        if event_index is not None:
            event_timestamps = pd.Series(rawdata[event_index]["time_stamps"])
            event_labels = rawdata[event_index]["time_series"]
            self.events = pd.DataFrame({
                'timestamp': event_timestamps - self.starttime,
                'label': event_labels
            })

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
