import spectHR as cs
from ipywidgets import Tab, Output
import pandas as pd
import pyhrv

def HRApp(DataSet):
    """
    Creates an interactive Heart Rate Variability (HRV) analysis application using ipywidgets.
    
    The application consists of multiple tabs for preprocessing, Poincaré plots, descriptive statistics, 
    power spectral density (PSD) plots, and epoch visualization (Gantt charts). Each tab dynamically updates 
    based on user interaction, displaying relevant analyses and visualizations.

    Parameters:
    ----------
    DataSet : object
        A spectHRdataset object containing RTop data such as inter-beat intervals (IBIs), epochs, and more. 

    Returns:
    -------
    None
        Displays the interactive GUI application within the notebook.
    """
    
    # Create the initial preprocessing GUI using spectHR's prepPlot method
    GUI = cs.prepPlot(DataSet, 500, 700)  # Set dimensions for the preprocessing GUI
    
    # Initialize Output widgets for different tabs
    preProcessing = Output()
    with preProcessing:
        display(GUI)  # Display the GUI for preprocessing in the first tab
    
    # Create placeholders for the remaining tabs
    poincarePlot = Output()
    psdPlot = Output()
    descriptives = Output()
    Gantt = Output()
    
    # Create the Tab widget with all the Output widgets as children
    App = Tab(children=[preProcessing, poincarePlot, descriptives, psdPlot, Gantt])
    
    # Set titles for each tab
    App.set_title(0, "PreProcessing")
    App.set_title(1, "Poincare")
    App.set_title(2, "Descriptives")
    App.set_title(3, "PSD")
    App.set_title(4, "Epochs")
    
    # Initialize empty series for PSD and descriptive statistics values
    DataSet.psd_Values = pd.Series()
    DataSet.descriptives_Values = pd.Series()
    
    # Define the callback function for handling tab switches
    def on_tab_change(change):
        """
        Callback function to handle tab changes in the HRV analysis application.
        
        Parameters:
        ----------
        change : dict
            A dictionary containing information about the change event. The key 'new' indicates
            the index of the newly selected tab.
        """
        if change['name'] == 'selected_index':        
            if change['new'] == 1:  # Poincare tab selected
                with poincarePlot:
                    poincarePlot.clear_output()  # Clear previous content
                    display(cs.poincare(DataSet))  # Display Poincare plot for the dataset
                
            if change['new'] == 2:  # Descriptives tab selected
                with descriptives:
                    descriptives.clear_output()  # Clear previous content
                    
                    # Compute descriptive statistics grouped by epoch
                    DataSet.descriptives_Values = cs.explode(DataSet)\
                        .groupby('epoch')['ibi']\
                        .agg([\
                            ('N', len),\
                            ('mean', 'mean'),\
                            ('std', 'std'),\
                            ('min', 'min'),\
                            ('max', 'max'),\
                            ('rmssd', lambda x: pyhrv.time_domain.rmssd(x)[0]), \
                            ('sdnn', lambda x: pyhrv.time_domain.sdnn(x)[0]),\
                            ('sdsd', cs.Tools.Params.sdsd),\
                            ('sd1', cs.Tools.Params.sd1),\
                            ('sd2', cs.Tools.Params.sd2),\
                            ('sd_ratio', cs.Tools.Params.sd_ratio),\
                            ('ellipse_area', cs.ellipse_area)\
                        ])
                    
                    # Merge PSD values if available
                    if hasattr(DataSet, 'psd_Values'):
                        df = pd.DataFrame(list(DataSet.psd_Values.dropna()))
                        df['epoch'] = DataSet.psd_Values.dropna().index
                        pd.set_option('display.precision', 8)  # Set display precision for DataFrame
                        DataSet.descriptives_Values = pd.merge(DataSet.descriptives_Values, df, on='epoch', how='outer')
                    
                    display(DataSet.descriptives_Values)  # Display the computed statistics
                    
            if change['new'] == 3:  # PSD tab selected
                with psdPlot:
                    psdPlot.clear_output()  # Clear previous content
                    
                    # Compute PSD values using Welch's method
                    Data = cs.explode(DataSet)
                    DataSet.psd_Values = Data.groupby('epoch')[Data.columns.tolist()]\
                                             .apply(cs.welch_psd, nperseg=256, noverlap=128)
                    
            if change['new'] == 4:  # Gantt tab selected
                with Gantt:
                    Gantt.clear_output()  # Clear previous content
                    display(cs.gantt(DataSet, labels=False))  # Display Gantt chart visualization
            
        # Save changes to the dataset after any tab interaction
        DataSet.save()
    
    # Attach the tab change observer to the Tab widget
    App.observe(on_tab_change, names='selected_index')
    
    # Display the complete Tab application
    display(App)
