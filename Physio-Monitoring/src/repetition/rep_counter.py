class RepCounter:
    """
    Counts exercise repetitions by tracking phase transitions.
    Uses proper hysteresis logic to avoid double-counting.
    One rep = complete movement cycle (extended -> flexed -> extended)
    """

    def __init__(self, min_angle, max_angle, movement_threshold=6):
        """
        Initialize repetition counter.
        
        Args:
            min_angle: Minimum angle for 'flexed' state (degrees)
            max_angle: Maximum angle for 'extended' state (degrees)
            movement_threshold: Minimum angle change to count as motion
        """
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.movement_threshold = movement_threshold

        self.prev_angle = None
        self.phase = None  # Will be initialized on first angle
        self.reps = 0
        self.has_reached_flexion = False  # Track if we've reached minimum flex angle

    def _initialize_phase(self, angle):
        """Initialize starting phase based on first angle"""
        if angle >= self.max_angle:
            self.phase = "extended"
        elif angle <= self.min_angle:
            self.phase = "flexed"
        else:
            # In between - assume extended
            self.phase = "extended"

    def update(self, angle, posture_ok=True):
        """
        Update counter with new angle measurement.
        
        Args:
            angle: Current joint angle in degrees
            posture_ok: Whether posture is correct for this rep (bool)
            
        Returns:
            Current repetition count (int)
        """
        # Initialize phase on first update
        if self.phase is None:
            self._initialize_phase(angle)
            self.prev_angle = angle
            return self.reps

        # Check for minimum motion to avoid noise
        delta = abs(angle - self.prev_angle)
        self.prev_angle = angle

        # Skip if movement below threshold
        if delta < self.movement_threshold:
            return self.reps
        
        # Only count reps if posture is correct
        if not posture_ok:
            return self.reps

        # CORRECTED STATE MACHINE LOGIC
        # =====================================
        
        if self.phase == "extended":
            # Extended state: waiting for joint to FLEX
            # Transition when angle drops BELOW max_angle
            if angle < self.max_angle:
                self.phase = "flexed"
                self.has_reached_flexion = False  # Reset - haven't reached full flex yet
        
        elif self.phase == "flexed":
            # Flexed state: must reach full flexion (angle <= min_angle)
            # Then extend back to complete the rep
            if angle <= self.min_angle:
                self.has_reached_flexion = True  # Mark that we reached full flexion
            
            # Complete rep only if we reached full flexion AND angle is extending back
            if angle > self.max_angle and self.has_reached_flexion:
                self.phase = "extended"
                self.reps += 1
                self.has_reached_flexion = False

        return self.reps
    
    def reset(self):
        """Reset counter to zero."""
        self.reps = 0
        self.phase = None
        self.prev_angle = None
        self.has_reached_flexion = False
