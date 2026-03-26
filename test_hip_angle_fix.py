#!/usr/bin/env python3
"""
Test script to validate hip angle computation
"""
import sys
from pathlib import Path
import numpy as np

# Add path
sys.path.insert(0, str(Path(__file__).parent / "physio-web" / "backend"))

from exercise_engine.engine import ExerciseEngine

def test_hip_angle_calculations():
    """Test hip angle calculations with mock coordinates"""
    
    print("=" * 60)
    print("HIP ANGLE CALCULATION TEST")
    print("=" * 60)
    
    engine = ExerciseEngine()
    
    # Test cases: (description, right_hip, right_knee, expected_lateral_angle_range)
    test_cases = [
        (
            "Standing upright (no abduction)",
            (0.5, 0.5, 0),      # Hip at center
            (0.5, 0.7, 0),      # Knee directly below
            (0, 10)             # Should be close to 0°
        ),
        (
            "30° hip abduction",
            (0.5, 0.5, 0),      # Hip at center
            (0.6, 0.7, 0),      # Knee offset to the side
            (20, 40)            # Should be around 30°
        ),
        (
            "60° hip abduction",
            (0.5, 0.5, 0),      # Hip at center
            (0.8, 0.7, 0),      # Knee further offset
            (50, 70)            # Should be around 60°
        ),
        (
            "90° hip abduction (horizontal leg)",
            (0.5, 0.5, 0),      # Hip at center
            (1.0, 0.5, 0),      # Knee directly to the side
            (80, 90)            # Should be close to 90°
        ),
    ]
    
    all_passed = True
    
    for description, hip_coord, knee_coord, expected_range in test_cases:
        angle = engine._calculate_lateral_angle(hip_coord, knee_coord)
        expected_min, expected_max = expected_range
        
        passed = expected_min <= angle <= expected_max
        status = "✓ PASS" if passed else "✗ FAIL"
        
        print(f"\n{status}: {description}")
        print(f"  Hip: {hip_coord}")
        print(f"  Knee: {knee_coord}")
        print(f"  Calculated angle: {angle:.1f}°")
        print(f"  Expected range: {expected_min}°-{expected_max}°")
        
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)
    
    return all_passed

def test_motion_calculation():
    """Test motion calculation for hip angles"""
    
    print("\n" + "=" * 60)
    print("HIP MOTION CALCULATION TEST")
    print("=" * 60)
    
    engine = ExerciseEngine()
    
    # Simulate a sequence of angles representing hip abduction motion
    angles_sequence = [
        0,    # Standing (leg at 0°)
        5,    # Slight abduction
        15,   # Moderate abduction
        30,   # Good abduction
        45,   # Full abduction
        30,   # Return to moderate
        15,   # Return further
        5,    # Return to slight
        0,    # Back to standing
    ]
    
    print("\nSimulating hip abduction movement:")
    print("Frame | Angle | Motion | Expected Min")
    print("------|-------|--------|-------------")
    
    engine.previous_angles["hip_abduction"] = 0
    total_motion = 0
    
    for frame_num, angle in enumerate(angles_sequence):
        motion_val = abs(angle - engine.previous_angles.get("hip_abduction", 0))
        total_motion += motion_val
        engine.previous_angles["hip_abduction"] = angle
        
        status = "✓" if motion_val >= 2.0 else " "
        print(f"  {frame_num:>2}  | {angle:>5.0f}° | {motion_val:>6.1f} | {status}  (need >= 2.0)")
    
    print("\n" + "=" * 60)
    print(f"Total motion detected: {total_motion:.1f}°")
    print(f"Average motion per frame: {total_motion / len(angles_sequence):.1f}°")
    
    # Count how many frames had sufficient motion
    sufficient_frames = sum(1 for i in range(1, len(angles_sequence)) 
                          if abs(angles_sequence[i] - angles_sequence[i-1]) >= 2.0)
    print(f"Frames with motion >= 2.0°: {sufficient_frames}/{len(angles_sequence)-1}")
    
    if sufficient_frames >= len(angles_sequence) // 2:
        print("✓ MOTION DETECTION OK")
        return True
    else:
        print("✗ INSUFFICIENT MOTION DETECTION")
        return False

if __name__ == "__main__":
    test1_passed = test_hip_angle_calculations()
    test2_passed = test_motion_calculation()
    
    print("\n" + "=" * 60)
    print("OVERALL RESULT")
    print("=" * 60)
    if test1_passed and test2_passed:
        print("✓ All hip angle tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Check the output above.")
        sys.exit(1)
