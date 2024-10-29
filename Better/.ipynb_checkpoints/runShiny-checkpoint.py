from shiny import App, ui, reactive, render
import matplotlib.pyplot as plt
import numpy as np
import spectHR as cs

# Load your data
data = cs.SpectHRDataset("Example Data/SUB_002.xdf", 1, event_index=0)
data = cs.borderData(data)
data.ecg = data.ecg.slicetime(500,560)
data = cs.filterECGData(data, {'filterType': 'highpass', 'cutoff': 1})
data = cs.calcPeaks(data)

# Shiny UI
app_ui = ui.page_fluid(
    ui.h2("ECG Plot with Editable R-tops"),
    ui.input_select("action_select", "Select Action", choices=["drag", "remove", "add"]),
    ui.output_plot("plot"),
    ui.input_slider("zoom_range", "Zoom X-axis", min=min(data.ecg.time), max=max(data.ecg.time),
                    value=(min(data.ecg.time), max(data.ecg.time)), width='100%')
)

# Shiny Server logic
def server(input, output, session):
    # Initialize R-tops
    r_tops = reactive.Value(data.ecg.RTopTimes.tolist())
    
    # Plot function
    @output
    @render.plot
    def plot():
        plt.figure(figsize=(10, 6))
        ax = plt.gca()  # Get current axes

        # Initialize LineHandler with the figure and axes
        line_handler = cs.LineHandler(fig=plt.gcf(), ax=ax, x=data.ecg.time, y=data.ecg.level)

        # Plot the ECG data
        plt.plot(data.ecg.time, data.ecg.level, label="ECG Signal")
        
        # Add draggable R-tops from the reactive R-tops
        for rtop in r_tops():  # Use parentheses to access reactive value
            line_handler.add_line(rtop, color='red', alpha=0.5)

        # Set x-axis limits based on zoom range
        zoom_range = input.zoom_range()
        plt.xlim(zoom_range)

        plt.title("ECG Signal with Draggable R-tops")
        plt.xlabel("Time")
        plt.ylabel("ECG Level")
        plt.legend()
        plt.grid(True)
        plt.show()

    # This function will handle the interaction when an R-top is dragged
    @reactive.Effect
    def update_rtops():
        action = input.action_select()
        # Handle dragging
        if action == "drag":
            selected_data = session.input.get("selectedData")  # Get the selected data
            if selected_data and 'points' in selected_data:
                new_x = selected_data['points'][0]['x']  # Get the x value of the selected point
                idx = np.argmin(np.abs(np.array(r_tops()) - new_x))  # Find the closest R-top
                line_handler.draggable_lines[idx].line.set_xdata([new_x])  # Update the position of the vertical line
                r_tops()[idx] = new_x  # Update the reactive value

        elif action == "add":
            new_rtop = input.zoom_range()[1]  # Example: adding at the right edge of the current zoom
            line_handler.add_line(new_rtop, color='red', alpha=0.5)  # Add a new draggable line
            r_tops().append(new_rtop)  # Update the reactive R-tops list
            r_tops().sort()  # Keep R-tops sorted

        elif action == "remove":
            if line_handler.draggable_lines:
                line_handler.remove_line(line_handler.draggable_lines[-1])  # Remove the last line
                r_tops().pop()  # Update the reactive R-tops list

# Create the Shiny app
app = App(app_ui, server)
