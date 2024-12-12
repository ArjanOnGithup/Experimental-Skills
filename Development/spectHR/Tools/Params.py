import numpy as np
import pyhrv

def sd1(ibi):
    ibi = np.asarray(ibi)
    return np.std(np.subtract(1000 * ibi[:-1],  1000 * ibi[1:]) / np.sqrt(2))
    
def sd2(ibi):
    ibi = np.asarray(ibi)
    return np.std(np.add(1000 * ibi[:-1],  1000 * ibi[1:]) / np.sqrt(2))

def sd_ratio(ibi):
    return sd1(ibi)/sd2(ibi)

def ellipse_area(ibi):
    return np.pi * sd1(ibi) *sd2(ibi)

def sdsd(ibi):
    try:
        ret = pyhrv.time_domain.sdsd(np.asarray(ibi))
    except:
        ret = np.nan
    return ret