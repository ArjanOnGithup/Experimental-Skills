import numpy as np

def sd1(ibi):
    ibi = np.asarray(ibi)
    return np.std(np.subtract(ibi[:-1],  ibi[1:]) / np.sqrt(2))
    
def sd2(ibi):
    ibi = np.asarray(ibi)
    return np.std(np.add(ibi[:-1],  ibi[1:]) / np.sqrt(2))
