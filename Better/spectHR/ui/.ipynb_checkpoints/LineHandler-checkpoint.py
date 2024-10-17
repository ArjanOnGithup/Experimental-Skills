from .DraggableVLine import DraggableVLine

class LineHandler:
    """
    Class to handle adding, dragging, and removing vertical lines on a plot,
    and manage interactive modes such as zoom, region selection, and finding maximums.

    Attributes:
        fig (matplotlib.figure.Figure): The matplotlib figure object.
        ax (matplotlib.axes.Axes): The axes of the plot.
        x (np.ndarray): The x data of the plot.
        y (np.ndarray): The y data of the plot.
        draggable_lines (list of DraggableVLine): List of draggable vertical lines on the plot.
        mode (str): The current interaction mode (e.g., 'drag', 'add', 'find').
        press (float or None): x-coordinate of the mouse press for region selection.
        shaded_area (matplotlib.patches.Polygon or None): Shaded region for actions like zoom or max-finding.
    """
    def __init__(self, fig, ax, x, y):
        """
        Initialize the LineHandler with a figure, axes, and data.

        Args:
            fig (matplotlib.figure.Figure): The figure object.
            ax (matplotlib.axes.Axes): The axes object.
            x (np.ndarray): The x-axis data.
            y (np.ndarray): The y-axis data.
        """
        self.fig = fig  # Store the figure object.
        self.ax = ax  # Store the axes object.
        self.x = x  # Store x data.
        self.y = y  # Store y data.
        self.draggable_lines = []  # List to store all draggable lines.
        self.mode = 'drag'  # Default mode for interaction.
        self.press = None  # To track the press state (for region selection).
        self.shaded_area = None  # To store the shaded area for selection actions.
        self.connect_events()

    def add_line(self, xdata, color='b', alpha=0.3):
        """
        Add a vertical line to the plot and make it draggable.

        Args:
            xdata (float): x-coordinate where the vertical line is added.
            color (str, optional): Color of the line. Defaults to 'b'.
            alpha (float, optional): Transparency level of the line. Defaults to 0.3.
        """
        line = self.ax.axvline(x=xdata, color=color, linestyle='-', alpha=alpha)  # Create vertical line.
        draggable_line = DraggableVLine(line)  # Make the line draggable.
        self.draggable_lines.append(draggable_line)  # Store in the list.
        self.fig.canvas.draw_idle()  # Redraw the canvas.
        

    def connect_events(self):
        """
        Connect the figure canvas events to the respective handler functions for mouse interactions.
        """
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def update_mode(self, change):
        """
        Update the interaction mode based on user input (e.g., radio button).

        Args:
            change (dict): Dictionary containing information about the mode change.
        """
        self.mode = change['new']  # Set mode to the new value.

    def on_click(self, event):
        """
        Handle mouse click events based on the current interaction mode.

        Args:
            event (matplotlib.backend_bases.Event): The mouse click event.
        """
        if self.mode == 'add':
            self.add_line(event.xdata, color='red')  # Add a red line at the clicked position.

        elif self.mode == 'drag':
            # Enable dragging for all lines.
            for line in self.draggable_lines:
                line.on_press(event)

        elif self.mode in ['find', 'zoom in', 'remove']:
            self.press = event.xdata  # Store starting x-coordinate for region selection.
            if self.shaded_area:
                self.shaded_area.remove()  # Remove previous shaded area, if any.
            # Create a new shaded area depending on mode.
            color = 'green' if self.mode == 'find' else ('blue' if self.mode == 'zoom in' else 'red')
            self.shaded_area = self.ax.axvspan(self.press, self.press, color=color, alpha=0.3)

    def on_motion(self, event):
        """
        Handle mouse motion events for region selection (zoom, find, or remove).

        Args:
            event (matplotlib.backend_bases.Event): The mouse motion event.
        """
        if self.press is None or self.mode not in ['find', 'zoom in', 'remove']:
            return  # Do nothing if no region is being selected.

        # Update shaded region as the mouse moves.
        self.shaded_area.set_xy([[self.press, 0], [self.press, 1], [event.xdata, 1], [event.xdata, 0]])
        self.fig.canvas.draw_idle()  # Redraw the canvas.

    def on_release(self, event):
        """
        Handle mouse release events and process actions like zoom, finding max, or removing lines.

        Args:
            event (matplotlib.backend_bases.Event): The mouse release event.
        """
        if self.mode == 'drag':
            for line in self.draggable_lines:
                line.on_release(event)  # Release all draggable lines.

        elif self.mode == 'find' and self.press is not None:
            start_x, end_x = sorted([self.press, event.xdata])  # Get the selected region.
            self._find_max_in_region(start_x, end_x)

        elif self.mode == 'zoom in' and self.press is not None:
            start_x, end_x = sorted([self.press, event.xdata])
            self._zoom_in_region(start_x, end_x)

        elif self.mode == 'remove' and self.press is not None:
            start_x, end_x = sorted([self.press, event.xdata])
            self._remove_lines_in_region(start_x, end_x)

        self.press = None  # Reset press state.
        if self.shaded_area:
            self.shaded_area.remove()  # Remove shaded area.
            self.shaded_area = None
        self.fig.canvas.draw_idle()  # Redraw the canvas.

    def _find_max_in_region(self, start_x, end_x):
        """
        Find the maximum y-value in the selected x-region and add a vertical line at the x-coordinate of the max.

        Args:
            start_x (float): Starting x-coordinate of the region.
            end_x (float): Ending x-coordinate of the region.
        """
        mask = (self.x >= start_x) & (self.x <= end_x)  # Mask for x-values in the selected region.
        if np.any(mask):
            x_in_region = self.x[mask]
            y_in_region = self.y[mask]
            max_x = x_in_region[np.argmax(y_in_region)]  # Find x corresponding to the max y.
            self.add_line(max_x, color='red')  # Add a red line at the maximum point.

    def _zoom_in_region(self, start_x, end_x):
        """
        Zoom into the selected x-region and adjust y-limits to fit the data.

        Args:
            start_x (float): Starting x-coordinate of the zoom region.
            end_x (float): Ending x-coordinate of the zoom region.
        """
        mask = (self.x >= start_x) & (self.x <= end_x)
        if np.any(mask):
            min_y, max_y = np.min(self.y[mask]), np.max(self.y[mask])
            self.update_plot_limits(start_x, end_x, min_y, max_y)

    def _remove_lines_in_region(self, start_x, end_x):
        """
        Remove all draggable lines within the selected x-region.

        Args:
            start_x (float): Starting x-coordinate of the removal region.
            end_x (float): Ending x-coordinate of the removal region.
        """
        to_remove = [line for line in self.draggable_lines if start_x <= line.line.get_xdata()[0] <= end_x]
        for line in to_remove:
            line.line.remove()  # Remove the line from the plot.
            self.draggable_lines.remove(line)  # Remove from the list of draggable lines.

    def update_plot_limits(self, min_x, max_x, min_y, max_y):
        """
        Update the plot limits for zoom or reset.

        Args:
            min_x (float): Minimum x-axis limit.
            max_x (float): Maximum x-axis limit.
            min_y (float): Minimum y-axis limit.
            max_y (float): Maximum y-axis limit.
        """
        self.ax.set_xlim(min_x, max_x)  # Set x-axis limits.
        self.ax.set_ylim(min_y, max_y)  # Set y-axis limits.
        self.fig.canvas.draw_idle()  # Redraw the canvas.