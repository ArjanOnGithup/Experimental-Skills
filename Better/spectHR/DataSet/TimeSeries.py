import pandas as pd

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
