import spectHR as cs

DataSet = cs.SpectHRDataset("Example Data/SUB_002.xdf", 1, event_index = 0) 
bDataSet = cs.borderData(DataSet)
bDataSet.ecg = bDataSet.ecg.slicetime(500,520)
fDataSet = cs.filterECGData(bDataSet, 
                          {'filterType': 'highpass', 
                           'cutoff': .1})

tDataSet = cs.calcPeaks(bDataSet)
import matplotlib.pyplot as plt
# plt.xkcd()

cs.spectHRplot(tDataSet)