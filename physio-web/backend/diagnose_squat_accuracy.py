#!/usr/bin/env python3
"""
Diagnose squat exercise accuracy issues
Test reps, angles, and quality scores
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from exercise_engine.engine import ExerciseEngine
import json

def test_squat_accuracy():
    """Test squat exercise accuracy"""
    
    print("\n" + "=" * 80)
    print("SQUAT EXERCISE ACCURACY DIAGNOSTIC TEST")
    print("=" * 80 + "\n")
    
    engine = ExerciseEngine()
    
    # Realistic squat motion with detailed frame-by-frame data
    squat_sequence = [
        # Standing position
        {"frame": 0, "angle": 175, "description": "Standing (nearly extended)"},
        {"frame": 1, "angle": 165, "description": "Starting to bend"},
        {"frame": 2, "angle": 150, "description": "Bending deeper"},
        {"frame": 3, "angle": 130, "description": "Half squat"},
        {"frame": 4, "angle": 110, "description": "Getting lower"},
        {"frame": 5, "angle": 95, "description": "Deep squat"},
        {"frame": 6, "angle": 90, "description": "Bottom of squat"},
        {"frame": 7, "angle": 95, "description": "Starting to rise"},
        {"frame": 8, "angle": 110, "description": "Rising up"},
        {"frame": 9, "angle": 130, "description": "Half way up"},
        {"frame": 10, "angle": 150, "description": "Almost standing"},
        {"frame": 11, "angle": 170, "description": "Standing (full extension)"},
    ]
    
    exercise = "Body Weight Squat"
    
    print(f"Exercise: {exercise}")
    print("-" * 80)
    print()
    
    for i, frame_data in enumerate(squat_sequence):
        angle = frame_data["angle"]
        description = frame_data["description"]
        
        state = engine.state_manager.get_state(exercise)
        motion = {"knee": abs(angle - squat_sequence[i-1]["angle"]) if i > 0 else 0}
        
        # Count reps
        reps, posture_msg = engine._count_reps_simple(exercise, angle, state, motion, "knee")
        
        # Calculate quality score
        quality_score = engine._calculate_quality_score(exercise, angle)
        
        # Update state
        engine.state_manager.update_state(
            exercise,
            reps=state.get('reps'),
            last_angle=state.get('last_angle'),
            phase=state.get('phase'),
            direction=state.get('direction'),
            counting=state.get('counting'),
            been_above=state.get('been_above'),
            been_below=state.get('been_below'),
            direction_set=state.get('direction_set'),
            peak_angle=state.get('peak_angle'),
            valley_angle=state.get('valley_angle'),
            exited_since_last=state.get('exited_since_last')
        )
        
        print(f"Frame {i:2d}: {description:25s}")
        print(f"  Angle: {angle:6.1f}° | Motion: {motion['knee']:5.1f}° | Reps: {reps} | Quality: {quality_score:6.1f}%")
        print(f"  Phase: {state.get('phase'):8s} | Message: {posture_msg}")
        print()
    
    print("=" * 80)
    print("TEST 2: Check angle clamping and quality score calculation")
    print("=" * 80 + "\n")
    
    # Test with extreme angles
    test_angles = [
        (50, "Below range (should be clamped)"),
        (85, "Bottom of squat (should have good quality)"),
        (100, "Mid-squat (should have excellent quality)"),
        (150, "Near standing (should have poor quality)"),
        (200, "Above range (should be clamped)"),
    ]
    
    for test_angle, description in test_angles:
        quality = engine._calculate_quality_score(exercise, test_angle)
        print(f"Angle: {test_angle:6.1f}° | {description:40s} | Quality: {quality:6.1f}%")
    
    print("\n" + "=" * 80)
    print("TEST 3: Check rep counting state machine")
    print("=" * 80 + "\n")
    
    # Reset for clean test
    engine.state_manager.reset_exercise(exercise)
    
    # Perform 2 complete squats
    double_squat = [
        180, 160, 120, 90, 120, 160, 180,  # First squat
        175, 155, 115, 95, 115, 155, 175,  # Second squat
    ]
    
    print("Performing 2 complete squats (14 frames):")
    print("-" * 80)
    
    for i, angle in enumerate(double_squat):
        state = engine.state_manager.get_state(exercise)
        motion = {"knee": abs(angle - double_squat[i-1]) if i > 0 else 0}
        
        reps, msg = engine._count_reps_simple(exercise, angle, state, motion, "knee")
        
        engine.state_manager.update_state(
            exercise,
            reps=state.get('reps'),
            last_angle=state.get('last_angle'),
            phase=state.get('phase'),
            direction=state.get('direction'),
            counting=state.get('counting'),
            been_above=state.get('been_above'),
            been_below=state.get('been_below'),
            direction_set=state.get('direction_set'),
            peak_angle=state.get('peak_angle'),
            valley_angle=state.get('valley_angle'),
            exited_since_last=state.get('exited_since_last')
        )
        
        status = "[REP COUNTED]" if reps > 0 and (i == 0 or double_squat[i] != double_squat[i-1]) else ""
        print(f"Frame {i:2d}: Angle={angle:3d}°, Phase={state.get('phase'):8s}, Reps={reps}, Motion={motion['knee']:5.1f}° {status}")
    
    final_state = engine.state_manager.get_state(exercise)
    print(f"\nFinal Result: {final_state.get('reps')} reps (expected: 2)")
    
    print("\n" + "=" * 80)
    print("ACCURACY ASSESSMENT")
    print("=" * 80 + "\n")
    
    if final_state.get('reps') >= 2:
        print("✅ Rep counting: ACCURATE")
    else:
        print("❌ Rep counting: INACCURATE (expected 2 reps)")
    
    # Check quality score accuracy in good form range
    good_form_quality = engine._calculate_quality_score(exercise, 100)
    if good_form_quality > 80:
        print("✅ Quality scoring: ACCURATE (good form detected correctly)")
    else:
        print(f"❌ Quality scoring: INACCURATE (good form at 100° shows {good_form_quality:.1f}% instead of >80%)")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    test_squat_accuracy()
