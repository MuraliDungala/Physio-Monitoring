#!/usr/bin/env python3
"""
Test script to debug shoulder angle computation and rep counting
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from exercise_engine.engine import ExerciseEngine
import numpy as np

def test_shoulder_angles():
    """Test what angle keys are produced for shoulder exercises"""
    engine = ExerciseEngine()
    
    # Create mock MediaPipe landmarks for a simple pose
    # Let's create a pose with both arms at different angles
    class MockLandmark:
        def __init__(self, x, y, z, visibility=1.0):
            self.x = x
            self.y = y
            self.z = z
            self.visibility = visibility
    
    # Create landmarks in landmark order (33 landmarks for pose)
    landmarks = [MockLandmark(0.5, 0.5, 0) for _ in range(33)]
    
    # Set specific key landmarks for shoulder abduction test
    # nose = 0, left_shoulder = 11, right_shoulder = 12
    # left_elbow = 13, right_elbow = 14, left_hip = 23, right_hip = 24
    
    landmarks[0].x, landmarks[0].y = 0.5, 0.3  # nose
    landmarks[11].x, landmarks[11].y = 0.3, 0.5  # left shoulder
    landmarks[12].x, landmarks[12].y = 0.7, 0.5  # right shoulder      landmarks[13].x, landmarks[13].y = 0.15, 0.6  # left elbow (elevated)
    landmarks[14].x, landmarks[14].y = 0.85, 0.6  # right elbow (elevated)
    landmarks[23].x, landmarks[23].y = 0.3, 0.8  # left hip
    landmarks[24].x, landmarks[24].y = 0.7, 0.8  # right hip
    
    coords, angles, motion = engine._extract_pose_data(landmarks)
    
    print("=" * 60)
    print("ANGLE COMPUTATION TEST RESULTS")
    print("=" * 60)
    print(f"\nComputed Angles Dictionary Keys:")
    for key in sorted(angles.keys()):
        print(f"  {key}: {angles[key]:.1f}°")
    
    print(f"\nChecking for bilateral shoulder angles:")
    bilateral_keys = [k for k in angles.keys() if 'shoulder' in k.lower()]
    print(f"  Found {len(bilateral_keys)} shoulder-related angle keys:")
    for key in sorted(bilateral_keys):
        print(f"    - {key}: {angles[key]:.1f}°")
    
    print(f"\nCoordinates extracted:")
    print(f"  Total coords: {len(coords)}")
    shoulder_coords = {k: v for k, v in coords.items() if 'shoulder' in k}
    print(f"  Shoulder coords: {shoulder_coords}")
    
    # Now test rep counting with Shoulder Abduction
    print("\n" + "=" * 60)
    print("REP COUNTING TEST")
    print("=" * 60)
    
    # Test with Shoulder Abduction - use more extreme angles that cross thresholds
    exercise = "Shoulder Abduction"
    
    # For Shoulder Abduction range (10, 140):
    # lower_threshold = 10 + 130*0.2 = 36°
    # upper_threshold = 140 - 130*0.2 = 114°
    # Need to go above 114 and back below 36 for one rep
    
    test_angles = [20, 40, 60, 80, 100, 120, 130, 120, 100, 80, 60, 40, 20, 10]  # Should count 1 rep
    
    for frame_num, angle_val in enumerate(test_angles):
        state = engine.state_manager.get_state(exercise)
        old_phase = state.get('phase', 'extended')
        old_reps = state.get('reps', 0)
        
        reps, msg = engine._count_reps_simple(exercise, angle_val, state, {}, "shoulder_abduction")
        
        engine.state_manager.update_state(exercise, 
            reps=reps,
            last_angle=state.get('last_angle', angle_val),
            phase=state.get('phase', 'extended'),
            direction=state.get('direction'),
            counting=state.get('counting'))
        
        # Show phase changes
        new_phase = state.get('phase', 'extended')
        phase_change = " -> FLEXED" if old_phase == 'extended' and new_phase == 'flexed' else ""
        phase_change += " -> EXTENDED" if old_phase == 'flexed' and new_phase == 'extended' else ""
        
        rep_change = f" [REP COUNTED]" if reps > old_reps else ""
        
        print(f"Frame {frame_num}: angle={angle_val:3.0f}°, phase={new_phase:8}, reps={reps}{phase_change}{rep_change}")
    
    print(f"\n📊 Final reps for {exercise}: {engine.state_manager.get_state(exercise)['reps']}")

if __name__ == "__main__":
    test_shoulder_angles()
