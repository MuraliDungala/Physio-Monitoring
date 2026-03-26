class QualityScore:
    """
    Computes exercise quality based on range of motion, smoothness, and control.
    """
    def __init__(self, min_angle, max_angle):
        """
        Initialize quality scorer.
        
        Args:
            min_angle: Minimum angle for the exercise
            max_angle: Maximum angle for the exercise
        """
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.angles = []

    def update(self, angle):
        """
        Add a new angle measurement.
        
        Args:
            angle: Current joint angle in degrees
        """
        # Only add valid angles
        if angle is not None and angle > 0:
            self.angles.append(angle)
            if len(self.angles) > 40:
                self.angles.pop(0)

    def compute(self):
        """
        Compute overall quality score (0-100).
        
        Factors:
        - ROM Score (50%): Achieved range of motion vs expected
        - Smoothness (30%): Consistency of motion (low jerk)
        - Control (20%): Absence of sudden angle changes
        
        Returns:
            Quality score 0-100 (int)
        """
        if len(self.angles) < 5:
            return 0

        # ROM Score: how much of the expected range was achieved
        achieved_rom = max(self.angles) - min(self.angles)
        ideal_rom = self.max_angle - self.min_angle
        rom_score = min(achieved_rom / ideal_rom, 1.0) * 100 if ideal_rom > 0 else 0

        # Smoothness: penalize large frame-to-frame differences
        diffs = [abs(self.angles[i] - self.angles[i-1]) for i in range(1, len(self.angles))]
        avg_diff = sum(diffs) / len(diffs) if diffs else 0
        smoothness = max(0, 100 - (avg_diff * 3))

        # Control: penalize jerks (sudden changes > 20 degrees per frame)
        jerks = sum(1 for d in diffs if d > 20)
        control = max(0, 100 - jerks * 10)

        # Weighted combination
        quality = int(0.5 * rom_score + 0.3 * smoothness + 0.2 * control)
        return min(100, max(0, quality))
    
    def reset(self):
        """Clear angle history."""
        self.angles = []
