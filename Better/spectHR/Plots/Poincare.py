import pyhrv
import matplotlib.pyplot as plt

def poincare(data, x_min=None, x_max=None):
    pyhrv.nonlinear.poincare(rpeaks = data.ecg.RTopTimes)
    