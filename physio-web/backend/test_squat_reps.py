#!/usr/bin/env python3
"""
Test squat rep counting with realistic motion
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from exercise_engine.engine import ExerciseEngine

def test_squat_reps():
    """Test squat rep counting with realistic motion"""
    
    print("\n" + "=" * 80)
    print("SQUAT REP COUNTING TEST - REALISTIC MOTION")
    print("=" * 80 + "\n")
    
    engine = ExerciseEngine()
    
    # Test 1: Body Weight Squat - full motion from standing to full squat
    print("✓ TEST 1: Body Weight Squat (full motion)")
    print("-" * 80)
    print("Expected: angle goes 180° -> 85° -> 180° (should count 1 rep)")
    print()
    
    # Generate realistic squat sequence
    # Standing (180°) -> Squatting (85°) -> Standing (180°)
    squat_sequence = [
        180, 170, 160, 140, 120, 100, 90, 85, 90, 100, 120, 140, 160, 170, 180
    ]
    
    exercise = "Body Weight Squat"
    reps = 0
    
    for i, angle in enumerate(squat_sequence):
        state = engine.state_manager.get_state(exercise)
        motion = {"knee": abs(angle - squat_sequence[i-1]) if i > 0 else 0}
        
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
        
        status = "✓" if reps > 0 else " "
        print(f"  Frame {i:2d}: Angle={angle:3d}°, Motion={motion['knee']:5.1f}°, Reps={reps}, Phase={state.get('phase')}")
    
    print(f"\n  Final Result: {reps} reps - {'✅ PASS' if reps >= 1 else '❌ FAIL'}")
    
    # Test 2: Partial Squat
    print("\n✓ TEST 2: Partial Squat (shallow motion)")
    print("-" * 80)
    print("Expected: angle goes 180° -> 110° -> 180° (should count 1 rep)")
    print()
    
    partial_squat = [180, 170, 160, 140, 120, 110, 120, 140, 160, 170, 180]
    
    exercise = "Partial Squat"
    reps = 0
    
    for i, angle in enumerate(partial_squat):
        state = engine.state_manager.get_state(exercise)
        motion = {"knee": abs(angle - partial_squat[i-1]) if i > 0 else 0}
        
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
        
        print(f"  Frame {i:2d}: Angle={angle:3d}°, Motion={motion['knee']:5.1f}°, Reps={reps}, Phase={state.get('phase')}")
    
    print(f"\n  Final Result: {reps} reps - {'✅ PASS' if reps >= 1 else '❌ FAIL'}")
    
    # Test 3: Wall Sit
    print("\n✓ TEST 3: Wall Sit (static hold)")
    print("-" * 80)
    print("Expected: angle stays around 90° (may or may not count as rep, depends on movement)")
    print()
    
    wall_sit = [180, 170, 150, 120, 100, 95, 95, 95, 95, 100, 120, 150, 170, 180]
    
    exercise = "Wall Sit"
    reps = 0
    
    for i, angle in enumerate(wall_sit):
        state = engine.state_manager.get_state(exercise)
        motion = {"knee": abs(angle - wall_sit[i-1]) if i > 0 else 0}
        
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
        
        print(f"  Frame {i:2d}: Angle={angle:3d}°, Motion={motion['knee']:5.1f}°, Reps={reps}, Phase={state.get('phase')}")
    
    print(f"\n  Final Result: {reps} reps")
    
    print("\n" + "=" * 80)
    print("✅ SQUAT REP COUNTING TEST COMPLETE")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_squat_reps()
