import pyhrv
import matplotlib.pyplot as plt

def poincare(data, xy_min=None, xy_max=None):
    ret = pyhrv.nonlinear.poincare(rpeaks = data.RTops['time'], legend=False)
    ret = ret.as_dict()
    fig = ret['poincare_plot']
    ax = fig.get_axes()
    ax=ax[0]
    if xy_min is not None and xy_max is not None:
        ax.set_xlim(xy_min, xy_max)
        ax.set_ylim(xy_min, xy_max)
    return ret
