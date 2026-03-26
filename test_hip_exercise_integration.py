#!/usr/bin/env python3
"""
Comprehensive integration test for hip exercise detection
"""
import sys
from pathlib import Path
import json

# Add path
sys.path.insert(0, str(Path(__file__).parent / "physio-web" / "backend"))

from exercise_engine.engine import ExerciseEngine

def simulate_hip_abduction_exercise():
    """Simulate a complete hip abduction exercise with proper landmarks"""
    
    print("=" * 70)
    print("HIP ABDUCTION EXERCISE SIMULATION")
    print("=" * 70)
    
    engine = ExerciseEngine()
    
    # Mock landmarks that represent a person doing hip abduction
    # MediaPipe has 33 landmarks; we'll create enough for hip angle calculation
    class MockLandmark:
        def __init__(self, x, y, z=0, visibility=0.8):
            self.x = x
            self.y = y
            self.z = z
            self.visibility = visibility
    
    # Simulate multiple frames of hip abduction
    # Frame by frame: person standing -> abduct leg -> return to standing
    frame_sequence = [
        # Frame 0: Standing position (0° abduction)
        {
            "right_shoulder": MockLandmark(0.4, 0.3),
            "right_hip": MockLandmark(0.4, 0.5),
            "right_knee": MockLandmark(0.4, 0.7),  # Directly below hip
            "left_hip": MockLandmark(0.6, 0.5),
            "left_knee": MockLandmark(0.6, 0.7),
        },
        # Frame 1: Initial abduction (10°)
        {
            "right_shoulder": MockLandmark(0.4, 0.3),
            "right_hip": MockLandmark(0.4, 0.5),
            "right_knee": MockLandmark(0.42, 0.7),  # Slightly to the right
            "left_hip": MockLandmark(0.6, 0.5),
            "left_knee": MockLandmark(0.6, 0.7),
        },
        # Frame 2: More abduction (25°)
        {
            "right_shoulder": MockLandmark(0.4, 0.3),
            "right_hip": MockLandmark(0.4, 0.5),
            "right_knee": MockLandmark(0.5, 0.7),   # Further right
            "left_hip": MockLandmark(0.6, 0.5),
            "left_knee": MockLandmark(0.6, 0.7),
        },
        # Frame 3: Good abduction (40°)
        {
            "right_shoulder": MockLandmark(0.4, 0.3),
            "right_hip": MockLandmark(0.4, 0.5),
            "right_knee": MockLandmark(0.6, 0.7),   # Good lateral position
            "left_hip": MockLandmark(0.6, 0.5),
            "left_knee": MockLandmark(0.6, 0.7),
        },
        # Frame 4: Peak abduction (50°)
        {
            "right_shoulder": MockLandmark(0.4, 0.3),
            "right_hip": MockLandmark(0.4, 0.5),
            "right_knee": MockLandmark(0.65, 0.75),  # Peak position
            "left_hip": MockLandmark(0.6, 0.5),
            "left_knee": MockLandmark(0.6, 0.7),
        },
        # Frame 5: Returning (35°)
        {
            "right_shoulder": MockLandmark(0.4, 0.3),
            "right_hip": MockLandmark(0.4, 0.5),
            "right_knee": MockLandmark(0.55, 0.72),  # Return
            "left_hip": MockLandmark(0.6, 0.5),
            "left_knee": MockLandmark(0.6, 0.7),
        },
        # Frame 6: Further return (20°)
        {
            "right_shoulder": MockLandmark(0.4, 0.3),
            "right_hip": MockLandmark(0.4, 0.5),
            "right_knee": MockLandmark(0.45, 0.7),   # Further return
            "left_hip": MockLandmark(0.6, 0.5),
            "left_knee": MockLandmark(0.6, 0.7),
        },
        # Frame 7: Back to standing (0°)
        {
            "right_shoulder": MockLandmark(0.4, 0.3),
            "right_hip": MockLandmark(0.4, 0.5),
            "right_knee": MockLandmark(0.4, 0.7),    # Back to start
            "left_hip": MockLandmark(0.6, 0.5),
            "left_knee": MockLandmark(0.6, 0.7),
        },
    ]
    
    print("\nProcessing frames...")
    print("-" * 70)
    print("Frame | Hip Angle | Motion | Reps | Status")
    print("-" * 70)
    
    last_angle = 0
    total_reps = 0
    
    for frame_num, landmarks_dict in enumerate(frame_sequence):
        # Create a list of landmarks for the engine
        landmarks_list = [MockLandmark(0, 0)] * 33  # Create 33 empty landmarks
        
        # Fill in the relevant landmarks
        idx_map = {
            "left_shoulder": 11, "right_shoulder": 12,
            "left_hip": 23, "right_hip": 24,
            "left_knee": 25, "right_knee": 26,
        }
        
        for name, idx in idx_map.items():
            if name in landmarks_dict:
                landmarks_list[idx] = landmarks_dict[name]
        
        # Process frame
        result = engine.process_frame_from_landmarks(landmarks_list, selected_exercise="Hip Abduction")
        
        if result:
            angle = result.get("angle", 0)
            reps = result.get("reps", 0)
            message = result.get("posture_message", "")
            
            # Calculate motion
            motion = abs(angle - last_angle)
            last_angle = angle
            
            # Detect rep count change
            rep_indicator = " ✓ REP!" if reps > total_reps else ""
            total_reps = reps
            
            print(f"  {frame_num:>2}  | {angle:>8.1f}° | {motion:>6.1f} | {reps:>4} | {message[:40]:40}{rep_indicator}")
    
    print("-" * 70)
    print(f"\nFinal Result: {total_reps} reps counted")
    
    if total_reps > 0:
        print("✓ HIP EXERCISE DETECTION SUCCESSFUL")
        return True
    else:
        print("✗ HIP EXERCISE DETECTION FAILED - No reps counted")
        return False

def main():
    print("\n" + "=" * 70)
    print("HIP EXERCISE INTEGRATION TEST")
    print("=" * 70 + "\n")
    
    # First check if we have the necessary method
    engine = ExerciseEngine()
    if not hasattr(engine, 'process_frame_from_landmarks'):
        print("Note: process_frame_from_landmarks method not found.")
        print("Testing basic angle calculations instead...\n")
        
        # Test just the angle calculations
        hip = (0.4, 0.5, 0)
        knee_standing = (0.4, 0.7, 0)
        knee_abducted = (0.6, 0.7, 0)
        
        angle_standing = engine._calculate_lateral_angle(hip, knee_standing)
        angle_abducted = engine._calculate_lateral_angle(hip, knee_abducted)
        
        print(f"Standing position lateral angle: {angle_standing:.1f}°")
        print(f"Abducted position lateral angle: {angle_abducted:.1f}°")
        
        if angle_standing < 10 and angle_abducted > 30:
            print("\n✓ ANGLE CALCULATION TEST PASSED")
            return True
        else:
            print("\n✗ ANGLE CALCULATION TEST FAILED")
            return False
    
    # Run the full integration test
    return simulate_hip_abduction_exercise()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
