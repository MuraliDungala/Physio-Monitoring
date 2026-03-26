"""
Test script to verify the two fixes:
1. Shoulder rep counting should count up+down as 1 rep (not 2)
2. Exit exercise button should properly clean up resources
"""

import sys
import os
import json
from exercise_engine.engine import ExerciseEngine
from exercise_state_manager import ExerciseStateManager

def test_shoulder_rep_counting():
    """Test that shoulder exercises count one rep per cycle (up+down = 1 rep)"""
    print("\n" + "="*60)
    print("TEST 1: Shoulder Rep Counting Fix")
    print("="*60)
    
    engine = ExerciseEngine()
    state_manager = ExerciseStateManager()
    
    # Test data: simulating a shoulder flexion rep
    # User lifts arm from 20° to 120° and back to 30°
    angles_sequence = [
        20,   # Starting position
        40,   # Lifting up
        60,   # Midpoint going up
        80,   # Continuing up
        100,  # Near max
        120,  # Peak position
        100,  # Coming down
        80,   # Continuing down
        60,   # Midpoint going down
        40,   # Almost back
        30,   # Rest position
        50,   # Lifting again for second rep
        90,
        120,  # Peak again
        60,   # Coming down
        30,   # Back to rest
    ]
    
    exercise = "Shoulder Flexion"
    reps_counted = []
    
    print(f"\nSimulating: {exercise} with angle sequence")
    print(f"Angles: {angles_sequence}")
    print(f"\nExpected: 2 complete reps (one per up+down cycle)")
    print("-" * 40)
    
    state = state_manager.get_state(exercise)
    state['counting'] = False
    state['reps'] = 0
    state['exited_since_last'] = True
    
    for i, angle in enumerate(angles_sequence):
        reps, msg = engine._count_reps_simple(exercise, angle, state)
        
        # Track when a new rep is counted
        if i > 0 and reps > len(reps_counted):
            reps_counted.append(reps)
            print(f"Frame {i:2d} | Angle: {angle:3.0f}° | Rep COUNTED: {reps} | {msg}")
        else:
            if i % 3 == 0:  # Print every 3rd frame for brevity
                print(f"Frame {i:2d} | Angle: {angle:3.0f}° | Reps: {reps} | {msg}")
    
    print("-" * 40)
    print(f"\nFinal Result: {reps} reps counted")
    print(f"Expected: 2 reps (one per complete cycle)")
    
    if reps == 2:
        print("✓ PASS: Shoulder rep counting is correct!")
        return True
    else:
        print(f"✗ FAIL: Expected 2 reps but got {reps}")
        return False


def test_exit_exercise_websocket_cleanup():
    """Test that exit exercise properly cleans up resources"""
    print("\n" + "="*60)
    print("TEST 2: Exit Exercise Button Cleanup")
    print("="*60)
    
    print("\nChecking exitExercise function in script.js...")
    print("-" * 40)
    
    frontend_script = "e:\\Physio-Monitoring\\physio-web\\frontend\\script.js"
    
    with open(frontend_script, 'r') as f:
        content = f.read()
        
    # Check if exitExercise properly closes websocket
    exit_func_start = content.find("function exitExercise()")
    exit_func_end = content.find("function ", exit_func_start + 1)
    exit_func = content[exit_func_start:exit_func_end]
    
    checks = {
        "Closes websocket": "websocket.close()" in exit_func,
        "Nullifies websocket": "websocket = null" in exit_func,
        "Clears currentExercise": "currentExercise = null" in exit_func,
        "Resets exerciseState": "exerciseState =" in exit_func,
        "Stops camera": "stopCamera()" in exit_func,
        "Closes pose": "pose.close()" in exit_func,
        "Navigates back": "showPage('exercises')" in exit_func,
    }
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}: {'Present' if passed else 'Missing'}")
        if not passed:
            all_passed = False
    
    print("-" * 40)
    
    if all_passed:
        print("✓ PASS: Exit exercise function properly cleans up!")
        return True
    else:
        print("✗ FAIL: Exit exercise function is missing cleanup steps")
        return False


def test_state_reset_on_rep_count():
    """Test that state is properly reset when a rep is counted"""
    print("\n" + "="*60)
    print("TEST 3: State Reset After Rep Count")
    print("="*60)
    
    engine = ExerciseEngine()
    
    # Simulate one complete rep: 20° -> 120° -> 30°
    angles = [20, 40, 60, 80, 100, 120, 100, 80, 60, 40, 30]
    
    exercise = "Shoulder Abduction"
    state = {
        'reps': 0,
        'counting': False,
        'been_above': False,
        'been_below': False,
        'direction_set': False,
        'exited_since_last': True,
        'peak_angle': 0,
        'valley_angle': 0,
        'last_angle': 20,
        'direction': None
    }
    
    print(f"\nSimulating: {exercise}")
    print("Tracking state reset after rep count...")
    print("-" * 40)
    
    for i, angle in enumerate(angles):
        reps, msg = engine._count_reps_simple(exercise, angle, state)
        
        if i == len(angles) - 1:  # Last frame
            print(f"\nAfter completing rep:")
            print(f"  Reps counted: {reps}")
            print(f"  counting flag: {state['counting']}")
            print(f"  been_above: {state['been_above']}")
            print(f"  been_below: {state['been_below']}")
            print(f"  direction_set: {state['direction_set']}")
            
            # For the next rep to start immediately, these should be False
            can_start_next = not state['been_above'] and not state['been_below'] and not state['direction_set']
            
            print(f"\nCan start next rep immediately: {can_start_next}")
            
            if can_start_next:
                print("✓ PASS: State properly reset for next rep!")
                return True
            else:
                print("✗ FAIL: State not properly reset")
                return False
    
    return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING SHOULDER REP COUNTING & EXIT BUTTON FIXES")
    print("="*60)
    
    results = []
    
    try:
        results.append(("Shoulder Rep Counting", test_shoulder_rep_counting()))
    except Exception as e:
        print(f"✗ ERROR in test 1: {e}")
        results.append(("Shoulder Rep Counting", False))
    
    try:
        results.append(("Exit Exercise Cleanup", test_exit_exercise_websocket_cleanup()))
    except Exception as e:
        print(f"✗ ERROR in test 2: {e}")
        results.append(("Exit Exercise Cleanup", False))
    
    try:
        results.append(("State Reset After Rep", test_state_reset_on_rep_count()))
    except Exception as e:
        print(f"✗ ERROR in test 3: {e}")
        results.append(("State Reset After Rep", False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("-" * 40)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED")
        sys.exit(1)
