import pandas as pd
import numpy as np
import pyxdf
from datetime import datetime

class TimeSeries:
    def __init__(self, x, y, srate=None):
        self.time = pd.Series(x)
        self.level = pd.Series(y)

        if srate is not None:
            self.srate = srate
        else:
            self.srate = round(1.0 / (self.time.diff().mean()))

    def slicetime(self, time_min, time_max):
        mask = (self.time >= time_min) & (self.time <= time_max)
        return TimeSeries(self.time.loc[mask], self.level.loc[mask], self.srate)

    def to_dataframe(self):
        return pd.DataFrame({"time": self.time, "level": self.level, "srate": self.srate})

class SpectHRDataset:
    def __init__(self, filename, ecg_index=1, br_index=None, event_index=None, par=None):
        self.ecg = None
        self.br = None
        self.events = None
        self.loadData(filename, ecg_index, br_index, event_index)
        self.history = []
        self.par = {}
        self.starttime = None

    def loadData(self, filename, ecg_index=None, br_index=None, event_index=None):
        rawdata, header = pyxdf.load_xdf(filename)

        if ecg_index is not None:
            ecg_x = pd.Series(rawdata[ecg_index]["time_stamps"])
            self.starttime = ecg_x[0]
            ecg_y = pd.Series(rawdata[ecg_index]["time_series"].flatten())
            ecg_x = ecg_x - self.starttime
            self.ecg = TimeSeries(ecg_x, ecg_y)

            
        if br_index is not None:
            br_x = pd.Series(rawdata[br_index]["time_stamps"])
            br_y = pd.Series(rawdata[br_index]["time_series"].flatten())
            br_x = br_x - self.starttime
            self.br = TimeSeries(br_x, br_y)

        if event_index is not None:
            event_timestamps = pd.Series(rawdata[event_index]["time_stamps"])
            event_labels = rawdata[event_index]["time_series"]
            self.events = pd.DataFrame({'timestamp': event_timestamps - self.starttime, 'label': event_labels})

    def log_action(self, action_name, params):
        log_entry = {
            'action': action_name,
            'timestamp': datetime.now(),
            'parameters': params
        }
        self.history.append(log_entry)