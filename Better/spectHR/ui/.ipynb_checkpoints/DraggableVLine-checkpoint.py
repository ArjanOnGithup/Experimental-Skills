import matplotlib.pyplot as plt

class DraggableVLine:
    """
    A class to manage a vertical line on a Matplotlib plot that can be dragged along the x-axis.

    This class provides interactivity for vertical lines in Matplotlib, allowing users to click 
    and drag the line along the x-axis. When the line is dragged, an optional callback function 
    can be triggered to handle updates or additional processing related to the new line position.

    Attributes:
    -----------
    line : matplotlib.lines.Line2D
        The vertical line to be made draggable.
    press : float or None
        Stores the x-coordinate where the mouse was pressed, used to determine the start of dragging.
    on_drag_callback : function or None
        A function to be called when the line drag ends, with the new x-coordinate passed as an argument.
    
    Methods:
    --------
    connect():
        Connects the event listeners for mouse press, motion, and release.
    on_press(event):
        Handles the mouse press event. Records the x-coordinate if the event occurs on the line.
    on_motion(event):
        Handles the mouse motion event. Updates the line's position as the mouse is dragged.
    on_release(event):
        Handles the mouse release event. Finalizes the drag and triggers the callback if provided.
    """
    
    def __init__(self, line, on_drag_callback=None):
        """
        Initializes a DraggableVLine instance.

        Parameters:
        -----------
        line : matplotlib.lines.Line2D
            The vertical line to be made draggable.
        on_drag_callback : function, optional
            A callback function that takes the new x-coordinate of the line as input.
        """
        self.line = line  # Reference to the matplotlib line object.
        self.press = None  # Variable to track whether the line is being dragged.
        self.on_drag_callback = on_drag_callback  # Optional callback function after drag.
        self.connect()  # Connect the event listeners to the line.

    def connect(self):
        """
        Connects the mouse event listeners (press, release, motion) to the line.

        This method establishes connections between the mouse events and the corresponding event handlers.
        The handlers are called whenever the user interacts with the plot.

        Events:
        -------
        - button_press_event: Triggers when the mouse is pressed down.
        - button_release_event: Triggers when the mouse button is released.
        - motion_notify_event: Triggers when the mouse is moved.
        """
        self.cidpress = self.line.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.line.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.line.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        """
        Handles the mouse press event.

        Checks if the mouse press occurred on the draggable line. If so, records the x-coordinate
        where the press occurred. If the press is outside the line's axes, or the press does not
        occur on the line, nothing happens.

        Parameters:
        -----------
        event : matplotlib.backend_bases.MouseEvent
            The mouse event containing information about the mouse click.
        """
        if event.inaxes != self.line.axes:  # Ensure the press is within the plot axes.
            return
        contains, _ = self.line.contains(event)  # Check if the press occurred on the line.
        if not contains:
            return
        self.press = event.xdata  # Store the x-coordinate where the press happened.

    def on_motion(self, event):
        """
        Handles the mouse motion event.

        Updates the line's position as the mouse is dragged, redrawing the plot with the new line position.
        This only occurs if a press event has been registered (i.e., the line is currently being dragged),
        and if the motion occurs within the plot's axes.

        Parameters:
        -----------
        event : matplotlib.backend_bases.MouseEvent
            The mouse event containing information about the mouse movement.
        """
        if self.press is None or event.inaxes != self.line.axes:  # Only drag if a press occurred.
            return
        self.line.set_xdata(event.xdata)  # Update the line's x-coordinate to follow the mouse.
        self.line.figure.canvas.draw_idle()  # Redraw the canvas without blocking.

    def on_release(self, event):
        """
        Handles the mouse release event.

        Finalizes the drag action, resetting the press state and calling the optional callback function,
        if provided, with the new x-coordinate of the line.

        Parameters:
        -----------
        event : matplotlib.backend_bases.MouseEvent
            The mouse event containing information about the mouse release.
        """
        self.press = None  # Reset the press state, ending the drag.
        if self.on_drag_callback:
            self.on_drag_callback(event.xdata)  # Trigger the callback with the final x-coordinate.
        self.line.figure.canvas.draw_idle()  # Redraw the canvas to finalize the new position.
