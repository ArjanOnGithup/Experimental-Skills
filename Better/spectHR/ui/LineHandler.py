import matplotlib.pyplot as plt
import matplotlib.patches as patches


class DraggableVLine:
    """
    A draggable vertical line on a plot.
    
    Attributes:
        line (matplotlib.lines.Line2D): The line object representing the vertical line.
        callback_drag (callable): Function to call when the line is dragged.
    """
    
    def __init__(self, ax, x_position, callback_drag=None, color = 'red'):
        """
        Initializes DraggableVLine at a specified x position.
        
        Args:
            ax (matplotlib.axes.Axes): The axes to place the vertical line on.
            x_position (float): The initial x-coordinate for the line.
            callback_drag (callable, optional): Callback for when the line is dragged.
        """
        self.ax = ax
        self.line = ax.axvline(x=x_position, color=color, linestyle='--', picker=True, alpha = .5)
        self.callback_drag = callback_drag
        self.press = None

    def on_press(self, event):
        """
        Captures the initial click location if near the line.
        
        Args:
            event (matplotlib.backend_bases.Event): The mouse press event.
        """

        if self.line.contains(event)[0]:
            self.press = event.xdata

    def on_drag(self, event):
        """
        Drags the line to follow the mouse's x position.
        
        Args:
            event (matplotlib.backend_bases.Event): The mouse drag event.
        """
        if self.press is None or event.inaxes != self.ax:
            return
            
        new_x = event.xdata
        self.line.set_xdata([new_x, new_x])
        plt.draw()
        
        # Callback with updated x-position if set
        if self.callback_drag:
            self.callback_drag(self, new_x)

    def on_release(self, event):
        """
        Releases the drag operation.
        
        Args:
            event (matplotlib.backend_bases.Event): The mouse release event.
        """
        
        self.press = None

    def connect(self, fig):
        """
        Connects events for dragging the line.
        
        Args:
            fig (matplotlib.figure.Figure): The figure in which to capture events.
        """
        fig.canvas.mpl_connect('button_press_event', self.on_press)
        fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        fig.canvas.mpl_connect('button_release_event', self.on_release)

class LineHandler:
    """
    Manages draggable lines on a plot, allowing add, remove, and drag operations.
    
    Attributes:
        draggable_lines (set): A set of DraggableVLine objects on the plot.
        callback_add (callable): Function to call when a line is added.
        callback_remove (callable): Function to call when a line is removed.
    """
    
    def __init__(self, fig, ax, callback_add=None, callback_remove=None, callback_drag=None):
        """
        Initializes LineHandler with an empty set of draggable lines and optional callbacks.
        
        Args:
            callback_add (callable, optional): Callback for when a line is added.
            callback_remove (callable, optional): Callback for when a line is removed.
            callback_drag (callable, optional): Callback for when a line is dragged.
        """
        self.draggable_lines = []
        self.callback_add = callback_add
        self.callback_remove = callback_remove
        self.callback_drag = callback_drag
        self.mode = 'Drag'

    def add_line(self, ax, x_position, color='red'):
        """
        Adds a draggable line at the specified x position without plotting it.
        
        Args:
            ax (matplotlib.axes.Axes): The axes on which to add the line.
            x_position (float): The x-coordinate for the new line.
        """
        line = DraggableVLine(ax, x_position, self.callback_drag, color=color)
        line.connect(ax.figure) 
        self.draggable_lines.append(line)
        

    def remove_line(self, line):
        """
        Removes a specified line from the set of draggable lines.
        
        Args:
            line (DraggableVLine): The line object to be removed.
        """
        if line in self.draggable_lines:
            line.line.remove()  # Remove line from the plot
            self.draggable_lines.discard(line)
            plt.draw()
            
            if self.callback_remove:
                self.callback_remove(line)
                
    def update_mode(self, mode):
        self.mode = mode

class AreaHandler:
    """
    Manages shaded area selection on the plot, supporting 'del' and 'find' operations.
    
    Attributes:
        mode (str): Mode of selection ('del' or 'find').
        start_x (float): X-coordinate of the selection start point.
        end_x (float): X-coordinate of the selection end point.
        patch (patches.Rectangle): The rectangle object representing the shaded area.
        callback_del (callable): Callback function for 'del' mode.
        callback_find (callable): Callback function for 'find' mode.
    """
    
    def __init__(self, fig, ax, callback_del = None, callback_find = None):
        """
        Initializes the AreaHandler with callbacks for 'del' and 'find' actions.
        
        Args:
            ax (matplotlib.axes.Axes): The axes on which to manage selections.
            callback_del (callable): Function to call when 'del' mode completes.
            callback_find (callable): Function to call when 'find' mode completes.
        """
        self.ax = ax
        self.mode = None
        self.start_x = None
        self.end_x = None
        self.patch = None
        self.callback_del = callback_del
        self.callback_find = callback_find
    
    def set_mode(self, mode):
        """
        Sets the mode for selection (either 'del' or 'find').
        
        Args:
            mode (str): The mode to set ('del' or 'find').
        """
        if mode not in ('Del', 'Find'):
            raise ValueError("Mode must be 'Del' or 'Find'.")
        self.mode = mode
    
    def on_press(self, event):
        """
        Starts a selection area when the mouse is pressed.
        
        Args:
            event (matplotlib.backend_bases.Event): The mouse press event.
        """
        if event.inaxes != self.ax or self.mode is None:
            return
        self.start_x = event.xdata
        self.patch = patches.Rectangle((self.start_x, self.ax.get_ylim()[0]),
                                       0, self.ax.get_ylim()[1] - self.ax.get_ylim()[0],
                                       color='gray', alpha=0.3)
        self.ax.add_patch(self.patch)
        plt.draw()
    
    def on_drag(self, event):
        """
        Updates the shaded selection area while the mouse is dragged.
        
        Args:
            event (matplotlib.backend_bases.Event): The mouse drag event.
        """
        if self.patch is None or event.inaxes != self.ax:
            return
        self.end_x = event.xdata
        width = self.end_x - self.start_x
        self.patch.set_width(width)
        plt.draw()
    
    def on_release(self, event):
        """
        Completes the selection area when the mouse is released and calls the appropriate callback.
        
        Args:
            event (matplotlib.backend_bases.Event): The mouse release event.
        """
        if self.patch is None or event.inaxes != self.ax:
            return
        self.end_x = event.xdata
        selected_range = (min(self.start_x, self.end_x), max(self.start_x, self.end_x))
        
        if self.mode == 'Del':
            self.callback_del(selected_range)
        elif self.mode == 'Find':
            self.callback_find(selected_range)
        
        self.ax.patches.remove(self.patch)
        self.patch = None
        plt.draw()
    
    def connect_events(self, fig):
        """
        Connects mouse events to AreaHandler for managing selections.
        
        Args:
            fig (matplotlib.figure.Figure): The figure in which to capture events.
        """
        fig.canvas.mpl_connect('button_press_event', self.on_press)
        fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        fig.canvas.mpl_connect('button_release_event', self.on_release)

'''
# Example usage
fig, ax = plt.subplots()

# LineHandler with callbacks for add/remove/drag events
line_handler = LineHandler(
    callback_add=lambda line: print(f"Added line at x={line.line.get_xdata()}"),
    callback_remove=lambda line: print(f"Removed line at x={line.line.get_xdata()}"),
    callback_drag=lambda line, x: print(f"Dragged line to x={x}")
)
line_handler.add_line(ax, x_position=5)

# AreaHandler with callbacks for selection ranges
area_handler = AreaHandler(
    ax,
    callback_del=lambda range: print(f"Deleting range: {range}"),
    callback_find=lambda range: print(f"Finding in range: {range}")
)
area_handler.set_mode('del')
area_handler.connect_events(fig)

plt.show()
'''