import pyhrv

def plot_psd(RTops = None):
    return RTops.groupby('epoch', group_keys=False)[RTops.columns.tolist()].apply(welch_psd, include_groups=True)

def welch_psd(RTops = None, mode = 'dev'):
    titlestring = RTops['epoch'].iloc[0]
    res = None
    try:
        res = pyhrv.frequency_domain.welch_psd(RTops['ibi'])
    except:
        pass

    if res is not None:
        pfig = res['fft_plot']
        pfig.set_figwidth(12)
        pfig.set_figheight(5)
        pfig.get_axes()[0].set_title(titlestring)
        pfig.get_axes()[0].set_ylim(0,.1)