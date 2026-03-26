#!/usr/bin/env python3
"""
Test that verifies the backend processes shoulder exercises correctly
This tests the hysteresis state machine directly
"""

import sys
import os

# Set up paths
sys.path.insert(0, os.getcwd())

from exercise_engine.engine import ExerciseEngine

def test_shoulder_flexion_one_complete_rep():
    """Test a complete shoulder flexion rep cycle"""
    print("="*70)
    print("TEST: Shoulder Flexion - One Complete Rep Cycle")
    print("="*70)
    
    # Simulate angle progression for one complete rep
    # Down from 30° to 120° and back to 30°
    angle_sequence = [
        30,   # Starting position
        40, 50, 60, 70,      # Moving up
        85, 100, 120,        # At full flexion
        110, 100, 85, 70, 60, 50,  # Moving down
        40, 30               # Back to start
    ]
    
    exercise_name = "Shoulder Flexion"
    
    print(f"\nProcessing {len(angle_sequence)} frames...")
    print(f"Exercise: {exercise_name}")
    print(f"Angle sequence: 30° → 120° → 30° (should = 1 rep)")
    print("-" * 70)
    
    try:
        engine = ExerciseEngine()
        state_manager = engine.state_manager
        
        rep_count = 0
        for i, angle in enumerate(angle_sequence):
            state = state_manager.get_state(exercise_name)
            reps, msg = engine._count_reps_simple(exercise_name, angle, state)
            
            # Persist state (critical!)
            state_manager.update_state(exercise_name,
                reps=state.get('reps', 0),
                last_angle=state.get('last_angle', 0),
                phase=state.get('phase', 'extended'),
                been_above=state.get('been_above', False),
                been_below=state.get('been_below', False),
                direction_set=state.get('direction_set', False),
                peak_angle=state.get('peak_angle', 0),
                valley_angle=state.get('valley_angle', 0),
                exited_since_last=state.get('exited_since_last', True)
            )
            
            if reps > rep_count:
                print(f"Frame {i:2d}: {angle:3d}° → REP {reps} COUNTED! {msg}")
                rep_count = reps
            elif i % 5 == 0:
                phase_str = state.get('phase', 'unknown')
                print(f"Frame {i:2d}: {angle:3d}° → {phase_str} phase")
        
        final_state = state_manager.get_state(exercise_name)
        final_reps = final_state['reps']
        
        print("-" * 70)
        print(f"\nFinal rep count: {final_reps}")
        print(f"Expected: 1 rep")
        
        if final_reps == 1:
            print("✓ PASS: Shoulder flexion counted 1 rep correctly!")
            return True
        else:
            print(f"✗ FAIL: Expected 1 rep but got {final_reps}")
            return False
    
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_shoulder_flexion_two_complete_reps():
    """Test two complete shoulder flexion rep cycles"""
    print("\n\n" + "="*70)
    print("TEST: Shoulder Flexion - Two Complete Rep Cycles")
    print("="*70)
    
    # Two complete cycles
    angle_sequence = [
        # Rep 1: Down from 30° to 120° and back
        30, 40, 50, 60, 70, 85, 100, 120, 110, 100, 85, 70, 60, 50, 40, 30,
        # Rep 2: Down from 30° to 120° and back
        35, 50, 70, 90, 110, 120, 115, 95, 70, 50, 35
    ]
    
    exercise_name = "Shoulder Flexion"
    
    print(f"\nProcessing {len(angle_sequence)} frames for 2 complete reps")
    print("-" * 70)
    
    try:
        engine = ExerciseEngine()
        state_manager = engine.state_manager
        
        rep_count = 0
        for i, angle in enumerate(angle_sequence):
            state = state_manager.get_state(exercise_name)
            reps, msg = engine._count_reps_simple(exercise_name, angle, state)
            
            # Persist state
            state_manager.update_state(exercise_name,
                reps=state.get('reps', 0),
                last_angle=state.get('last_angle', 0),
                phase=state.get('phase', 'extended'),
                been_above=state.get('been_above', False),
                been_below=state.get('been_below', False),
                direction_set=state.get('direction_set', False),
                peak_angle=state.get('peak_angle', 0),
                valley_angle=state.get('valley_angle', 0),
                exited_since_last=state.get('exited_since_last', True)
            )
            
            if reps > rep_count:
                print(f"Frame {i:2d}: {angle:3d}° → ⭐ REP {reps} COUNTED! {msg}")
                rep_count = reps
            elif i % 6 == 0:
                phase_str = state.get('phase', 'unknown')
                print(f"Frame {i:2d}: {angle:3d}° → {phase_str} phase")
        
        final_state = state_manager.get_state(exercise_name)
        final_reps = final_state['reps']
        
        print("-" * 70)
        print(f"\nFinal rep count: {final_reps}")
        print(f"Expected: 2 reps")
        
        if final_reps == 2:
            print("✓ PASS: Two reps counted correctly!")
            return True
        else:
            print(f"✗ FAIL: Expected 2 reps but got {final_reps}")
            return False
    
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🔴 SHOULDER REP COUNTING TEST SUITE")
    print("Testing backend rep counting with hysteresis state machine\n")
    
    results = []
    
    results.append(("One Rep Cycle", test_shoulder_flexion_one_complete_rep()))
    results.append(("Two Rep Cycles", test_shoulder_flexion_two_complete_reps()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("-" * 70)
    print(f"Result: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("✓✓✓ ALL TESTS PASSED!")
        print("The backend is correctly counting shoulder flexion reps.")
        print("Each rep cycle counts as 1 rep (not 2).")
    else:
        print("✗✗✗ SOME TESTS FAILED")
        print("Check the output above for details.")
