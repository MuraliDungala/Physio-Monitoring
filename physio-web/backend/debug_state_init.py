#!/usr/bin/env python3
"""
Debug squat rep counting state initialization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from exercise_engine.engine import ExerciseEngine

def test_state_init():
    """Debug state initialization"""
    
    print("\n" + "=" * 80)
    print("STATE INITIALIZATION DEBUG")
    print("=" * 80 + "\n")
    
    engine = ExerciseEngine()
    exercise = "Body Weight Squat"
    
    print(f"Exercise: {exercise}")
    print(f"Range: 60-110°, Midpoint: 85°")
    print()
    
    # First frame - should initialize state
    print(">>> First frame at 180°:")
    state_before = engine.state_manager.get_state(exercise)
    print(f"   State before: {state_before}")
    print(f"   'phase' in state: {'phase' in state_before}")
    
    # Call the function
    reps, msg = engine._count_reps_simple(
        exercise, 
        180,  # angle
        state_before, 
        {"knee": 0},  # motion
        "knee"  # angle_key
    )
    
    print(f"   Phase after first call: {state_before.get('phase')}")
    print(f"   Message: {msg}")
    print()
    
    # Second frame - should use initialized state
    print(">>> Second frame at 170°:")
    state_second = engine.state_manager.get_state(exercise)
    print(f"   State: {state_second}")
    print(f"   Current phase: {state_second.get('phase')}")
    
    reps, msg = engine._count_reps_simple(
        exercise, 
        170,  # angle
        state_second, 
        {"knee": 10},  # motion
        "knee"  # angle_key
    )
    
    print(f"   Phase after second call: {state_second.get('phase')}")
    print(f"   Reps: {reps}")
    print()
    
    # Check state persistence
    print(">>> Checking state persistence:")
    engine.state_manager.update_state(
        exercise,
        reps=state_second.get('reps', 0),
        last_angle=state_second.get('last_angle'),
        phase=state_second.get('phase'),
        direction=state_second.get('direction'),
        counting=state_second.get('counting'),
        been_above=state_second.get('been_above'),
        been_below=state_second.get('been_below'),
        direction_set=state_second.get('direction_set'),
        peak_angle=state_second.get('peak_angle'),
        valley_angle=state_second.get('valley_angle'),
        exited_since_last=state_second.get('exited_since_last')
    )
    
    state_after_update = engine.state_manager.get_state(exercise)
    print(f"   State after update: {state_after_update}")
    print(f"   Phase persisted: {state_after_update.get('phase')}")

if __name__ == "__main__":
    test_state_init()
