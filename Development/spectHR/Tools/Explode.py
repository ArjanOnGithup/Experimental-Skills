def explode(DataSet):
    if hasattr(DataSet, 'active_epochs') and isinstance(DataSet.active_epochs, dict):
        # If active_epochs exists, use it for filtering
        visible_epochs = {epoch: visible for epoch, visible in DataSet.active_epochs.items() if visible}
    else:
        # If active_epochs does not exist, show all epochs
        visible_epochs = {epoch: True for epoch in DataSet.unique_epochs}
        
    #filtered_data = DataSet.RTops[DataSet.RTops['epoch'].isin(visible_epochs.keys())]
    # Assuming 'DataSet.RTops' is your DataFrame and 'visible_epochs' is your dictionary
    visible_epochs_set = set(visible_epochs.keys())  # Convert the keys (epoch names) to a set
    
     # Step 1: Filter the 'epoch' list to only include visible epochs
    filtered_data = DataSet.RTops[DataSet.RTops['epoch'].apply(lambda x: any(epoch in visible_epochs_set for epoch in x))]
    
    # Step 2: Filter out only the visible epochs from each 'epoch' list
    filtered_data.loc[:, 'epoch'] = filtered_data['epoch'].apply(lambda x: [epoch for epoch in x if epoch in visible_epochs_set])
    
    # Step 3: Explode the 'epoch' lists into individual rows, now only with visible epochs
    exploded_data = filtered_data.explode('epoch')
    
    return exploded_data.dropna(subset=['ibi'])
    