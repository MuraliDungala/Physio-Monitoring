#!/usr/bin/env python3
"""
Test script to debug hip angle computation and rep counting
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from exercise_engine.engine import ExerciseEngine
import numpy as np

def test_hip_angles():
    """Test what angle is computed for hip exercises"""
    engine = ExerciseEngine()
    
    # Create mock MediaPipe landmarks for a simple pose
    class MockLandmark:
        def __init__(self, x, y, z, visibility=1.0):
            self.x = x
            self.y = y
            self.z = z
            self.visibility = visibility
    
    # Create landmarks in landmark order (33 landmarks for pose)
    landmarks = [MockLandmark(0.5, 0.5, 0) for _ in range(33)]
    
    # Set specific key landmarks
    # Define pose for Hip Abduction - legs spread apart
    landmarks[0].x, landmarks[0].y = 0.5, 0.3   # nose
    landmarks[11].x, landmarks[11].y = 0.3, 0.5  # left shoulder
    landmarks[12].x, landmarks[12].y = 0.7, 0.5  # right shoulder
    landmarks[23].x, landmarks[23].y = 0.35, 0.8  # left hip (slightly inward)
    landmarks[24].x, landmarks[24].y = 0.65, 0.8  # right hip (slightly inward)
    landmarks[25].x, landmarks[25].y = 0.25, 1.0  # left knee (spread out)
    landmarks[26].x, landmarks[26].y = 0.75, 1.0  # right knee (spread out)
    
    coords, angles, motion = engine._extract_pose_data(landmarks)
    
    print("=" * 60)
    print("HIP ANGLE COMPUTATION TEST")
    print("=" * 60)
    
    print(f"\nAll angles computed:")
    for key in sorted(angles.keys()):
        if 'hip' in key.lower() or key == 'hip':
            print(f"  {key}: {angles[key]:.1f}°")
    
    print(f"\nLooking specifically for 'hip' key:")
    if "hip" in angles:
        print(f"  hip: {angles['hip']:.1f}°")
    else:
        print(f"  'hip' key NOT FOUND in angles")
    
    print(f"\nBilateral hip angles:")
    print(f"  right_hip: {angles.get('right_hip', 'NOT COMPUTED')}")
    print(f"  left_hip: {angles.get('left_hip', 'NOT COMPUTED')}")
    
    # Test with different pose - legs together
    print("\n" + "=" * 60)
    print("TESTING WITH LEGS TOGETHER POSE")
    print("=" * 60)
    
    landmarks2 = [MockLandmark(0.5, 0.5, 0) for _ in range(33)]
    landmarks2[0].x, landmarks2[0].y = 0.5, 0.3
    landmarks2[11].x, landmarks2[11].y = 0.3, 0.5
    landmarks2[12].x, landmarks2[12].y = 0.7, 0.5
    landmarks2[23].x, landmarks2[23].y = 0.48, 0.8  # left hip (centered)
    landmarks2[24].x, landmarks2[24].y = 0.52, 0.8  # right hip (centered)
    landmarks2[25].x, landmarks2[25].y = 0.48, 1.0  # left knee (together)
    landmarks2[26].x, landmarks2[26].y = 0.52, 1.0  # right knee (together)
    
    coords2, angles2, motion2 = engine._extract_pose_data(landmarks2)
    
    print(f"\nBilateral hip angles (legs together):")
    print(f"  right_hip: {angles2.get('right_hip', 'NOT COMPUTED')}")
    print(f"  left_hip: {angles2.get('left_hip', 'NOT COMPUTED')}")
    print(f"  hip: {angles2.get('hip', 'NOT COMPUTED')}")
    
    # Test rep counting with Hip Abduction
    print("\n" + "=" * 60)
    print("HIP ABDUCTION REP COUNTING TEST")
    print("=" * 60)
    
    exercise = "Hip Abduction"
    
    # For Hip Abduction range (5, 75):
    # lower_threshold = 5 + 70*0.2 = 19°
    # upper_threshold = 75 - 70*0.2 = 61°
    # Need to go above 61 and back below 19 for one rep
    
    test_angles = [10, 20, 30, 40, 50, 60, 70, 60, 50, 40, 30, 20, 10]
    
    for frame_num, angle_val in enumerate(test_angles):
        state = engine.state_manager.get_state(exercise)
        old_reps = state.get('reps', 0)
        
        reps, msg = engine._count_reps_simple(exercise, angle_val, state, {}, "hip")
        
        engine.state_manager.update_state(exercise, 
            reps=reps,
            last_angle=state.get('last_angle', angle_val),
            phase=state.get('phase', 'extended'),
            direction=state.get('direction'),
            counting=state.get('counting'))
        
        rep_change = f" [REP #{reps}]" if reps > old_reps else ""
        print(f"Frame {frame_num}: angle={angle_val:3.0f}°, reps={reps}, phase={state.get('phase', 'extended'):8}{rep_change}")
    
    print(f"\nFinal reps for {exercise}: {engine.state_manager.get_state(exercise)['reps']}")

if __name__ == "__main__":
    test_hip_angles()
