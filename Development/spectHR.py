import spectHR as cs
import pyhrv

DataSet = cs.SpectHRDataset("Example Data/SUB_002.xdf", 1, event_index = 0) 
bDataSet = cs.borderData(DataSet)
bDataSet.ecg = bDataSet.ecg.slicetime(500,2100)
fDataSet = cs.filterECGData(bDataSet, 
                          {'filterType': 'highpass', 
                           'cutoff': 1})
tDataSet = cs.calcPeaks(bDataSet)
GUI = cs.spectplot(tDataSet, 860, 890)
