"""
Updated shoulder rep counters with correct angle ranges for 0-180° measurements
"""

class ShoulderRepCounter:
    """Base class for shoulder exercise rep counting with 0-180° angles"""
    
    def __init__(self, min_angle, max_angle, movement_threshold=5):
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.movement_threshold = movement_threshold
        self.prev_angle = None
        self.phase = "extended"
        self.reps = 0
        self.partial_reps = 0
    
    def update(self, angle, posture_ok=True):
        if self.prev_angle is None:
            self.prev_angle = angle
            return self.reps
        
        delta = abs(angle - self.prev_angle)
        self.prev_angle = angle
        
        if delta < self.movement_threshold:
            return self.reps
        
        if not posture_ok:
            return self.reps
        
        # Calculate midpoint threshold to prevent double-counting
        midpoint = (self.min_angle + self.max_angle) / 2
        
        # HYSTERESIS: Transition to flexed when reaching max_angle threshold
        if angle >= self.max_angle and self.phase == "extended":
            self.phase = "flexed"
            self.partial_reps += 1
        
        # HYSTERESIS: Complete rep only when crossing back below midpoint
        # This prevents double-counting by requiring full return journey
        elif angle <= midpoint and self.phase == "flexed":
            self.phase = "extended"
            self.reps += 1
        
        return self.reps
    
    def reset(self):
        self.reps = 0
        self.partial_reps = 0
        self.phase = "extended"
        self.prev_angle = None


# ============= SHOULDER EXERCISES (0-180° angle range) =============

class ShoulderFlexionCounter(ShoulderRepCounter):
    """Shoulder flexion: arm raising forward from 0° to 170°"""
    def __init__(self, movement_threshold=5):
        super().__init__(
            min_angle=30,       # Arm at side (relaxed)
            max_angle=140,      # Arm raised forward
            movement_threshold=movement_threshold
        )


class ShoulderAbductionCounter(ShoulderRepCounter):
    """Shoulder abduction: arm raising sideways from 0° to 170°"""
    def __init__(self, movement_threshold=5):
        super().__init__(
            min_angle=30,       # Arm at side
            max_angle=140,      # Arm raised sideways
            movement_threshold=movement_threshold
        )


class ShoulderExtensionCounter(ShoulderRepCounter):
    """Shoulder extension: arm extending backward"""
    def __init__(self, movement_threshold=5):
        super().__init__(
            min_angle=40,       # Neutral
            max_angle=100,      # Extended backward
            movement_threshold=movement_threshold
        )


class ShoulderAdductionCounter(ShoulderRepCounter):
    """Shoulder adduction: arm returning to body"""
    def __init__(self, movement_threshold=5):
        super().__init__(
            min_angle=30,       # Arm to body
            max_angle=140,      # Arm away
            movement_threshold=movement_threshold
        )


class ShoulderInternalRotationCounter(ShoulderRepCounter):
    """Shoulder internal rotation"""
    def __init__(self, movement_threshold=4):
        super().__init__(
            min_angle=50,       # Neutral
            max_angle=140,      # Full rotation
            movement_threshold=movement_threshold
        )


class ShoulderExternalRotationCounter(ShoulderRepCounter):
    """Shoulder external rotation"""
    def __init__(self, movement_threshold=4):
        super().__init__(
            min_angle=20,       # Neutral
            max_angle=120,      # Full rotation
            movement_threshold=movement_threshold
        )


class ShoulderHorizontalAbductionCounter(ShoulderRepCounter):
    """Shoulder horizontal abduction: arm moving backward"""
    def __init__(self, movement_threshold=5):
        super().__init__(
            min_angle=40,       # Neutral
            max_angle=120,      # Arm back
            movement_threshold=movement_threshold
        )


class ShoulderHorizontalAdductionCounter(ShoulderRepCounter):
    """Shoulder horizontal adduction: arm moving forward/across"""
    def __init__(self, movement_threshold=5):
        super().__init__(
            min_angle=30,       # Neutral
            max_angle=130,      # Arm across
            movement_threshold=movement_threshold
        )


class ShoulderCircumductionCounter(ShoulderRepCounter):
    """Shoulder circumduction: circular arm movement"""
    def __init__(self, movement_threshold=5):
        super().__init__(
            min_angle=60,       # Starting angle
            max_angle=170,      # Full circle movement
            movement_threshold=movement_threshold
        )


def create_shoulder_counter(exercise_name):
    """Factory function to create shoulder rep counter"""
    exercise_map = {
        "Shoulder Flexion": ShoulderFlexionCounter,
        "Shoulder Extension": ShoulderExtensionCounter,
        "Shoulder Abduction": ShoulderAbductionCounter,
        "Shoulder Adduction": ShoulderAdductionCounter,
        "Shoulder Internal Rotation": ShoulderInternalRotationCounter,
        "Shoulder External Rotation": ShoulderExternalRotationCounter,
        "Shoulder Horizontal Abduction": ShoulderHorizontalAbductionCounter,
        "Shoulder Horizontal Adduction": ShoulderHorizontalAdductionCounter,
        "Shoulder Circumduction": ShoulderCircumductionCounter,
    }
    
    if exercise_name in exercise_map:
        return exercise_map[exercise_name]()
    else:
        raise ValueError(f"Unknown exercise: {exercise_name}")
