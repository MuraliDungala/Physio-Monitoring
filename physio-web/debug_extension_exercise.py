"""
Debug script to trace extension exercise rep counting
"""
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Physio-Monitoring'))

from exercise_engine.engine import ExerciseEngine

def debug_exercise(exercise, angles, expected_reps):
    """Debug rep counting for a specific exercise"""
    print(f"\n{'='*70}")
    print(f"DEBUGGING: {exercise}")
    print(f"Angles: {angles}")
    print(f"Expected reps: {expected_reps}")
    print(f"{'='*70}")
    
    engine = ExerciseEngine()
    state = {'reps': 0, 'last_angle': 0, 'direction': None, 'counting': False}
    
    for i, angle in enumerate(angles):
        reps, msg = engine._count_reps_simple(exercise, angle, state)
        
        print(f"\nFrame {i}: angle={angle:.1f}°")
        print(f"  State: reps={reps}, counting={state.get('counting')}, "
              f"direction={state.get('direction')}")
        if state.get('counting'):
            print(f"  Peak: {state.get('peak_angle', 0):.1f}°, "
                  f"Valley: {state.get('valley_angle', 0):.1f}°")
        print(f"  Message: {msg}")
    
    actual_reps = reps
    print(f"\n{'='*70}")
    print(f"RESULT: Got {actual_reps} reps, expected {expected_reps}")
    print(f"Status: {'PASS' if actual_reps == expected_reps else 'FAIL'}")
    print(f"{'='*70}")

if __name__ == "__main__":
    # Debug the extension exercises
    debug_exercise('Elbow Extension', [160, 140, 100, 70, 100, 140, 160], 1)
    debug_exercise('Knee Extension', [160, 150, 120, 80, 120, 150, 160], 1)
    debug_exercise('Wrist Flexion', [20, 35, 55, 80, 55, 35, 20], 1)
    debug_exercise('Wrist Extension', [80, 55, 35, 20, 35, 55, 80], 1)
