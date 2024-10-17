from matplotlib import pyplot as plt
import ipywidgets as widgets
from ipywidgets import HBox, VBox
from ..ui.LineHandler import LineHandler

def spectHRplot(data, x_min=None, x_max=None):
    if x_min is None:
        x_min = data.ecg.time.min()
    if x_max is None:
        x_max = data.ecg.time.max()

    if data.br is not None:
        fig, (ax_ecg, ax_br) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    else:
        fig, ax_ecg = plt.subplots(figsize=(12, 6))

    line_handler = LineHandler(fig, ax_ecg, data.ecg.time, data.ecg.level)

    def update_plot():
        time = data.ecg.time
        level = data.ecg.level

        # Mask the time range
        mask = (time >= x_min) & (time <= x_max)
        num_points = mask.sum()

        # Downsample if necessary for better performance
        if num_points > 1000:
            factor = max(1, num_points // 1000)
            time = time[mask][::factor]
            level = level[mask][::factor]
        else:
            time = time[mask]
            level = level[mask]

        ax_ecg.clear()
        ax_ecg.plot(time, level, label='ECG Signal', color='blue')

        # Plot draggable lines for RTopTimes if they exist
        if hasattr(data.ecg, 'RTopTimes'):
            RTopTimes = data.ecg.RTopTimes
#            if len(RTopTimes) <= 20:
            for rtop in RTopTimes:
                if x_min <= rtop <= x_max:
                    line_handler.add_line(rtop, color = 'r')

        ax_ecg.set_title('ECG Signal')
        ax_ecg.set_xlabel('Time (seconds)')
        ax_ecg.set_ylabel('ECG Level (mV)')
        ax_ecg.set_xlim(x_min, x_max)
        ax_ecg.grid()

        # If the BR timeseries exists, plot it in the subplot
        if data.br is not None:
            br_time = data.br.time
            br_level = data.br.level
            mask_br = (br_time >= x_min) & (br_time <= x_max)
            num_points_br = mask_br.sum()

            # Downsample BR data if necessary
            if num_points_br > 1000:
                factor_br = max(1, num_points_br // 1000)
                br_time = br_time[mask_br][::factor_br]
                br_level = br_level[mask_br][::factor_br]
            else:
                br_time = br_time[mask_br]
                br_level = br_level[mask_br]

            ax_br.clear()
            ax_br.plot(br_time, br_level, label='Breathing Signal', color='green')
            ax_br.set_ylabel('Breathing Level')
            ax_br.grid()

        fig.canvas.draw_idle()

    update_plot()

    # Functions to zoom, pan, and update both axes
    def zoom_in(b):
        nonlocal x_min, x_max
        x_center = (x_min + x_max) / 2
        x_range = (x_max - x_min) / 2
        x_min = max(0, x_center - x_range / 2)
        x_max = min(data.ecg.time.max(), x_center + x_range / 2)
        update_plot()

    def zoom_out(b):
        nonlocal x_min, x_max
        x_range = (x_max - x_min) * 2
        x_min = max(0, x_min - x_range / 4)
        x_max = min(data.ecg.time.max(), x_max + x_range / 4)
        update_plot()

    def move_left(b):
        nonlocal x_min, x_max
        move_amount = (x_max - x_min) / 4
        x_min = max(0, x_min - move_amount)
        x_max = min(data.ecg.time.max(), x_max - move_amount)
        update_plot()

    def move_right(b):
        nonlocal x_min, x_max
        move_amount = (x_max - x_min) / 4
        x_min = max(0, x_min + move_amount)
        x_max = min(data.ecg.time.max(), x_max + move_amount)
        update_plot()

    # Buttons for zoom and panning controls
    zoom_in_button = widgets.Button(description="Zoom In")
    zoom_out_button = widgets.Button(description="Zoom Out")
    move_left_button = widgets.Button(description="Move Left")
    move_right_button = widgets.Button(description="Move Right")

    zoom_in_button.on_click(zoom_in)
    zoom_out_button.on_click(zoom_out)
    move_left_button.on_click(move_left)
    move_right_button.on_click(move_right)

    button_box = HBox([zoom_in_button, zoom_out_button, move_left_button, move_right_button])
    
    # Add the radio button to select interaction mode
    mode_radio_buttons = widgets.RadioButtons(
        options=['drag', 'add', 'find', 'zoom in', 'remove'],
        description='Mode:',
        disabled=False
    )

    # Link the radio button selection to update the mode in LineHandler
    mode_radio_buttons.observe(lambda change: line_handler.update_mode(change), names='value')

    # Combine buttons and radio buttons in the layout
    control_box = VBox([mode_radio_buttons, button_box])

    display(control_box)