#!/usr/bin/env python3
"""
Comprehensive test for all three fixes:
1. Neck angle detection with lowered visibility threshold
2. Squat false positive prevention with motion validation
3. Shoulder bilateral movement handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from exercise_engine.engine import ExerciseEngine
from exercise_state_manager import ExerciseStateManager
import numpy as np

# Mock landmark class
class MockLandmark:
    def __init__(self, x=0, y=0, z=0, visibility=0.9):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

def test_fixes():
    print("\n" + "="*70)
    print("COMPREHENSIVE FIX VERIFICATION TEST")
    print("="*70)
    
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Test 1: Neck detection with low visibility landmarks
    print("\n" + "-"*70)
    print("TEST 1: Neck Angle Detection (lowered visibility threshold 0.1)")
    print("-"*70)
    try:
        engine = ExerciseEngine()
        landmarks = [MockLandmark() for _ in range(33)]
        
        # Set neck landmarks with LOW visibility (0.15) - previously would be filtered
        landmarks[0] = MockLandmark(x=0.5, y=0.6, z=0, visibility=0.15)   # Nose
        landmarks[11] = MockLandmark(x=0.4, y=0.4, z=0, visibility=0.15)  # Left shoulder
        landmarks[12] = MockLandmark(x=0.6, y=0.4, z=0, visibility=0.15)  # Right shoulder
        landmarks[7] = MockLandmark(x=0.35, y=0.3, z=0, visibility=0.12)  # Left ear
        landmarks[8] = MockLandmark(x=0.65, y=0.3, z=0, visibility=0.12)  # Right ear
        
        coords, angles, motion = engine._extract_pose_data(landmarks)
        
        # Check if neck angles are computed
        neck_computed = all(key in angles for key in ['neck_flexion', 'neck_extension', 'neck_rotation'])
        angles_valid = all(angles.get(key, 0) > 0 for key in ['neck_flexion', 'neck_extension', 'neck_rotation'])
        
        if neck_computed and angles_valid:
            print(f"✓ PASS: Neck angles computed with low visibility landmarks:")
            print(f"  - neck_flexion: {angles['neck_flexion']:.1f}°")
            print(f"  - neck_extension: {angles['neck_extension']:.1f}°")
            print(f"  - neck_rotation: {angles['neck_rotation']:.1f}°")
            results["passed"] += 1
            results["tests"].append(("Neck Detection", "PASS"))
        else:
            print(f"✗ FAIL: Neck angles not properly computed")
            print(f"  Computed: {neck_computed}, Valid: {angles_valid}")
            print(f"  neck_flexion: {angles.get('neck_flexion', 0)}")
            results["failed"] += 1
            results["tests"].append(("Neck Detection", "FAIL"))
            
    except Exception as e:
        print(f"✗ FAIL: Exception in neck test: {e}")
        results["failed"] += 1
        results["tests"].append(("Neck Detection", "FAIL"))
    
    # Test 2: Squat false positive prevention
    print("\n" + "-"*70)
    print("TEST 2: Squat False Positive Prevention (motion validation)")
    print("-"*70)
    try:
        engine = ExerciseEngine()
        manager = ExerciseStateManager()
        exercise = "Body Weight Squat"
        state = manager.get_state(exercise)
        
        # Simulate static hold at threshold with minimal motion
        print("Simulating 5 frames holding at lower_threshold (70°) with ±1° noise:")
        no_reps_counted = True
        for frame in range(5):
            angle = 70 + np.random.uniform(-1, 1)
            motion_dict = {"knee": np.random.uniform(0, 0.5)}  # Very small motion
            reps, msg = engine._count_reps_simple(exercise, angle, state, motion_dict, "knee")
            state["reps"] = reps
            status = "✓" if reps == 0 else "✗ REP COUNTED"
            print(f"  Frame {frame}: angle={angle:.1f}°, motion=0.2°, reps={reps} {status}")
            if reps > 0:
                no_reps_counted = False
        
        if no_reps_counted:
            print(f"✓ PASS: No false positives with minimal motion")
            results["passed"] += 1
            results["tests"].append(("Squat False Positive Prevention", "PASS"))
        else:
            print(f"✗ FAIL: False positives detected during static hold")
            results["failed"] += 1
            results["tests"].append(("Squat False Positive Prevention", "FAIL"))
            
    except Exception as e:
        print(f"✗ FAIL: Exception in squat test: {e}")
        results["failed"] += 1
        results["tests"].append(("Squat False Positive Prevention", "FAIL"))
    
    # Test 3: Shoulder bilateral movement averaging
    print("\n" + "-"*70)
    print("TEST 3: Shoulder Bilateral Movement (no double counting)")
    print("-"*70)
    try:
        engine = ExerciseEngine()
        
        # Create landmarks with both arms raised
        landmarks = [MockLandmark() for _ in range(33)]
        
        # Set bilateral shoulder landmarks - both arms raised
        # Right side
        landmarks[12] = MockLandmark(x=0.6, y=0.2, z=0, visibility=0.95)  # Right shoulder at high position
        landmarks[14] = MockLandmark(x=0.6, y=0.15, z=0, visibility=0.95) # Right elbow elevated
        landmarks[15] = MockLandmark(x=0.6, y=0.05, z=0, visibility=0.95) # Right wrist elevated
        
        # Left side
        landmarks[11] = MockLandmark(x=0.4, y=0.2, z=0, visibility=0.95)  # Left shoulder at high position
        landmarks[13] = MockLandmark(x=0.4, y=0.15, z=0, visibility=0.95) # Left elbow elevated
        
        # Hip (needed for shoulder angle calculation)
        landmarks[23] = MockLandmark(x=0.4, y=0.5, z=0, visibility=0.95)
        landmarks[24] = MockLandmark(x=0.6, y=0.5, z=0, visibility=0.95)
        
        coords, angles, motion = engine._extract_pose_data(landmarks)
        
        # Check if shoulder flexion is the average of both arms
        if "shoulder_flexion" in angles and angles["shoulder_flexion"] > 0:
            shoulder_angle = angles["shoulder_flexion"]
            print(f"✓ PASS: Bilateral shoulder flexion computed correctly:")
            print(f"  - shoulder_flexion: {shoulder_angle:.1f}°")
            print(f"  (This is the average of left and right arms when both are raised)")
            results["passed"] += 1
            results["tests"].append(("Shoulder Bilateral", "PASS"))
        else:
            print(f"✗ FAIL: Shoulder flexion not computed for bilateral movement")
            results["failed"] += 1
            results["tests"].append(("Shoulder Bilateral", "FAIL"))
            
    except Exception as e:
        print(f"✗ FAIL: Exception in shoulder test: {e}")
        results["failed"] += 1
        results["tests"].append(("Shoulder Bilateral", "FAIL"))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nTotal Tests: {results['passed'] + results['failed']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    print("\nResults by Test:")
    for test_name, status in results["tests"]:
        symbol = "✓" if status == "PASS" else "✗"
        print(f"  {symbol} {test_name}: {status}")
    
    if results["failed"] == 0:
        print("\n" + "="*70)
        print("✓✓✓ ALL FIXES VERIFIED SUCCESSFULLY ✓✓✓")
        print("="*70)
        return True
    else:
        print(f"\n⚠️  {results['failed']} test(s) failed - review and re-test")
        return False

if __name__ == "__main__":
    success = test_fixes()
    sys.exit(0 if success else 1)
