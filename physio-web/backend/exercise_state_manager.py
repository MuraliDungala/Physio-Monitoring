"""
Exercise State Manager
Manages state for all exercises independently to support simultaneous multi-exercise tracking
"""

class ExerciseStateManager:
    """Manages exercise state with full isolation between exercises"""
    
    def __init__(self):
        self.states = {}  # {exercise_name: state_dict}
    
    def get_state(self, exercise_name: str) -> dict:
        """Get or create state for an exercise"""
        if exercise_name not in self.states:
            self.states[exercise_name] = {
                'reps': 0,
                'last_angle': 0,
                'direction': None,
                'counting': False,
                'session_start': None,
                'total_time': 0,
                'last_rep_time': 0,
                'quality_scores': [],
                'angle_history': [],
                # Hysteresis state machine fields
                'phase': 'extended',  # Two-phase tracking: extended or flexed
                'been_above': False,
                'been_below': False,
                'direction_set': False,
                'peak_angle': 0,
                'valley_angle': 0,
                'exited_since_last': True
            }
        return self.states[exercise_name]
    
    def reset_exercise(self, exercise_name: str):
        """Reset state for specific exercise"""
        self.states[exercise_name] = {
            'reps': 0,
            'last_angle': 0,
            'direction': None,
            'counting': False,
            'session_start': None,
            'total_time': 0,
            'last_rep_time': 0,
            'quality_scores': [],
            'angle_history': [],
            # Hysteresis state machine fields
            'phase': 'extended',
            'been_above': False,
            'been_below': False,
            'direction_set': False,
            'peak_angle': 0,
            'valley_angle': 0,
            'exited_since_last': True
        }
    
    def update_state(self, exercise_name: str, **kwargs):
        """Update specific fields in exercise state"""
        state = self.get_state(exercise_name)
        for key, value in kwargs.items():
            if key in state:
                state[key] = value
    
    def get_all_states(self):
        """Get all exercise states"""
        return self.states.copy()
    
    def clear_all(self):
        """Clear all states"""
        self.states.clear()
    
    def has_exercise(self, exercise_name: str) -> bool:
        """Check if exercise state exists"""
        return exercise_name in self.states
