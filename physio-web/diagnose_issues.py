#!/usr/bin/env python3
"""
Diagnostic script to identify the three reported issues:
1. Neck exercises not showing metrics
2. Squat false positives
3. Shoulder 2-hand double counting
"""

import sys
import os

# Add path to src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from exercise_engine.engine import ExerciseEngine
from exercise_state_manager import ExerciseStateManager
import numpy as np

# Simple mock landmark class
class MockLandmark:
    def __init__(self, x=0, y=0, z=0, visibility=0.9):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

def test_neck_detection():
    """Test if neck angles are being computed"""
    print("\n" + "="*60)
    print("TEST 1: NECK ANGLE DETECTION")
    print("="*60)
    
    engine = ExerciseEngine()
    
    # Create mock landmarks (simulating a pose with head tilted forward)
    landmarks = [MockLandmark() for _ in range(33)]
    
    # Set key landmarks with high visibility
    # Nose (index 0) - below shoulders (flexion)
    landmarks[0] = MockLandmark(x=0.5, y=0.6, z=0, visibility=0.95)
    
    # Right Shoulder (index 12)
    landmarks[12] = MockLandmark(x=0.6, y=0.4, z=0, visibility=0.95)
    
    # Left Shoulder (index 11)
    landmarks[11] = MockLandmark(x=0.4, y=0.4, z=0, visibility=0.95)
    
    # Left Ear (index 7)
    landmarks[7] = MockLandmark(x=0.35, y=0.3, z=0, visibility=0.95)
    
    # Right Ear (index 8)
    landmarks[8] = MockLandmark(x=0.65, y=0.3, z=0, visibility=0.95)
    
    # Extract coordinates and angles
    coords, angles, motion = engine._extract_pose_data(landmarks)
    
    print(f"\nDetected landmarks: {list(coords.keys())}")
    print(f"\nComputed angles (showing neck values):")
    for key in ['neck_flexion', 'neck_extension', 'neck_rotation']:
        if key in angles:
            print(f"  {key}: {angles[key]:.1f}°")
        else:
            print(f"  {key}: NOT COMPUTED")
    
    print(f"\nAll computed angles: {list(angles.keys())}")
    
    # Test if required landmarks were detected
    required_for_neck = ['nose', 'left_shoulder', 'right_shoulder', 'left_ear', 'right_ear']
    detected = [lm for lm in required_for_neck if lm in coords]
    print(f"\nNeck landmarks detected: {detected}/{len(required_for_neck)}")


def test_squat_false_positives():
    """Test if squat exercises count reps without motion"""
    print("\n" + "="*60)
    print("TEST 2: SQUAT FALSE POSITIVES")
    print("="*60)
    
    engine = ExerciseEngine()
    manager = ExerciseStateManager()
    
    # Simulate a static squat position (70° knee angle - at lower threshold)
    # For "Body Weight Squat", ranges are (60, 110°)
    # Lower threshold = 60 + (110-60)*0.2 = 70°
    # Upper threshold = 110 - (110-60)*0.2 = 100°
    
    exercise = "Body Weight Squat"
    
    # Get properly initialized state from manager
    state = manager.get_state(exercise)
    
    print(f"\nExercise: {exercise}")
    print("Rep count sequence while holding at 70° (lower threshold):")
    
    for frame in range(10):
        # Small noise around 70° - no real movement
        angle = 70 + np.random.uniform(-1, 1)  # Noise ±1°
        reps, msg = engine._count_reps_simple(exercise, angle, state)
        state["reps"] = reps  # Update the state
        print(f"  Frame {frame}: angle={angle:.1f}°, reps={reps}, phase={state.get('phase')}, msg={msg}")
        
        if reps > 0 and frame > 0:
            print(f"    ⚠️  FALSE POSITIVE: Rep counted with minimal motion!")


def test_shoulder_double_count():
    """Test if shoulder 2-hand exercises double-count reps"""
    print("\n" + "="*60)
    print("TEST 3: SHOULDER 2-HAND DOUBLE COUNTING")
    print("="*60)
    
    engine = ExerciseEngine()
    manager = ExerciseStateManager()
    
    exercise = "Shoulder Flexion"
    state = manager.get_state(exercise)
    
    print(f"\nExercise: {exercise}")
    print("Simulating continuous bilateral arm raise (both arms together):")
    
    # Shoulder flexion range: (10, 140°)
    # Lower threshold = 10 + (140-10)*0.2 = 36°
    # Upper threshold = 140 - (140-10)*0.2 = 114°
    
    angle_sequence = [20, 50, 80, 110, 140, 110, 80, 50, 20, 50, 80, 110, 140, 110, 80, 50, 20]
    
    for i, angle in enumerate(angle_sequence):
        reps, msg = engine._count_reps_simple(exercise, angle, state)
        state["reps"] = reps
        if reps > 0 and i > 0:  
            print(f"  Frame {i}: angle={angle:.1f}°, reps={reps} ⚠️  REP COUNTED")
        else:
            print(f"  Frame {i}: angle={angle:.1f}°, reps={reps}")


if __name__ == "__main__":
    print("\nDIAGNOSTIC TESTS FOR THREE REPORTED ISSUES")
    print("=" * 60)
    
    try:
        test_neck_detection()
    except Exception as e:
        print(f"ERROR in neck test: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_squat_false_positives()
    except Exception as e:
        print(f"ERROR in squat test: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_shoulder_double_count()
    except Exception as e:
        print(f"ERROR in shoulder test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("DIAGNOSTIC TESTS COMPLETE")
    print("="*60)
