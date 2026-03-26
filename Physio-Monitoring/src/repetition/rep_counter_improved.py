"""
Improved Repetition Counter with proper hysteresis zones.

For elbow flexion:
- Extended zone: angle >= EXTENDED_THRESHOLD (arm nearly straight, ~140°+)
- Transition zone: Between min and max 
- Flexed zone: angle <= FLEXED_THRESHOLD (arm bent, ~90°-)

State machine with hysteresis:
1. Start in extended state if angle >= max_angle
2. Transition to flexed only when angle drops below max_angle
3. Complete rep when angle rises above min_angle, return to extended
4. Hysteresis prevents rapid state switching in transition zone
"""

class RepCounterImproved:
    """
    Improved repetition counter with proper hysteresis logic.
    Uses threshold-based state machine to accurately count reps.
    
    Rep definition: Complete cycle from extended → flexed → extended
    """

    def __init__(self, min_angle, max_angle, movement_threshold=6):
        """
        Initialize improved repetition counter.
        
        Args:
            min_angle: Minimum angle when joint is fully flexed (degrees)
            max_angle: Maximum angle when joint is fully extended (degrees)
            movement_threshold: Minimum angle change to count as motion
        """
        self.min_angle = min_angle      # ~70° for elbow flexion (bent)
        self.max_angle = max_angle      # ~140° for elbow flexion (straight)
        self.movement_threshold = movement_threshold

        self.prev_angle = None
        self.phase = None               # Will be initialized on first angle
        self.reps = 0
        self.has_reached_flexion = False  # Track if we've reached minimum flex angle

    def _initialize_phase(self, angle):
        """Initialize starting phase based on first angle"""
        if angle >= self.max_angle:
            self.phase = "extended"
        elif angle <= self.min_angle:
            self.phase = "flexed"
        else:
            # In between - assume extended (closer to starting position)
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
        
        # Don't count during incorrect posture
        if not posture_ok:
            return self.reps

        # STATE MACHINE WITH PROPER HYSTERESIS
        # =====================================
        
        if self.phase == "extended":
            # In extended state: waiting for joint to FLEX
            # Transition when angle drops BELOW max_angle
            if angle < self.max_angle:
                self.phase = "flexed"
                self.has_reached_flexion = False  # Reset flag - haven't reached full flex yet
        
        elif self.phase == "flexed":
            # In flexed state: must reach full flexion (angle <= min_angle)
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
    
    def get_state(self):
        """Debug: Return current state information"""
        return {
            "phase": self.phase,
            "reps": self.reps,
            "prev_angle": self.prev_angle,
            "has_reached_flexion": self.has_reached_flexion
        }
