class MovingAverage:
    """
    Moving average filter for smoothing numeric values (angles, coordinates).
    """
    def __init__(self, window_size=5):
        """
        Initialize moving average filter.
        
        Args:
            window_size: Number of samples to average (larger = smoother but more latency)
        """
        self.window_size = window_size
        self.values = []

    def update(self, value):
        """
        Add new value and return smoothed average.
        
        Args:
            value: New numeric value to add
            
        Returns:
            Smoothed average of all values in window
        """
        self.values.append(value)
        if len(self.values) > self.window_size:
            self.values.pop(0)
        return sum(self.values) / len(self.values)
    
    def reset(self):
        """Clear the buffer."""
        self.values = []
    
    def is_stable(self, threshold=2.0):
        """
        Check if recent values are stable (low variance).
        
        Args:
            threshold: Maximum std deviation to consider stable
            
        Returns:
            True if stable, False otherwise
        """
        if len(self.values) < 3:
            return False
        avg = sum(self.values) / len(self.values)
        variance = sum((v - avg) ** 2 for v in self.values) / len(self.values)
        return variance ** 0.5 <= threshold


class CoordinateFilter:
    """
    Spatial filter for smoothing 2D coordinates (x, y).
    """
    def __init__(self, window_size=5):
        """
        Initialize coordinate filter.
        
        Args:
            window_size: Number of frames to average
        """
        self.window_size = window_size
        self.x_values = []
        self.y_values = []
    
    def update(self, coord):
        """
        Add new coordinate and return smoothed version.
        
        Args:
            coord: Tuple (x, y) representing a 2D point
            
        Returns:
            Smoothed (x, y) tuple
        """
        if coord is None:
            return None
        
        x, y = coord
        self.x_values.append(x)
        self.y_values.append(y)
        
        if len(self.x_values) > self.window_size:
            self.x_values.pop(0)
            self.y_values.pop(0)
        
        smooth_x = sum(self.x_values) / len(self.x_values)
        smooth_y = sum(self.y_values) / len(self.y_values)
        return (smooth_x, smooth_y)
    
    def reset(self):
        """Clear the buffers."""
        self.x_values = []
        self.y_values = []
