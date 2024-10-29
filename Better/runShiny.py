import spectHR as cs

DataSet = cs.SpectHRDataset("Example Data/SUB_002.xdf", 1, event_index = 0) 
bDataSet = cs.borderData(DataSet)
fDataSet = cs.filterECGData(bDataSet, 
                          {'filterType': 'highpass', 
                           'cutoff': 1})
tDataSet = cs.calcPeaks(bDataSet)
cs.spectHRplot(tDataSet)
