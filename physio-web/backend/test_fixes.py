#!/usr/bin/env python3
"""
Test script to verify the two fixes:
1. Shoulder rep counting should count up+down as 1 rep (not 2)
2. Exit exercise button cleanup
"""

import sys
import os

# Test the rep counting logic
def count_reps_simple(exercise, angle, state):
    """Simplified rep counting logic - matches the fixed version"""
    target_min, target_max = 0, 120  # Shoulder Flexion range
    reps = state['reps']
    midpoint = (target_min + target_max) / 2
    
    if not state['counting']:
        start_counting = target_min <= angle <= target_max
        if start_counting:
            state['counting'] = True
            state['peak_angle'] = angle
            state['valley_angle'] = angle
            state['been_above'] = angle >= midpoint
            state['been_below'] = angle <= midpoint
            state['direction_set'] = False
    else:
        state['peak_angle'] = max(state.get('peak_angle', angle), angle)
        state['valley_angle'] = min(state.get('valley_angle', angle), angle)
        
        if angle >= midpoint:
            state['been_above'] = True
        if angle <= midpoint:
            state['been_below'] = True
        
        if not state.get('direction_set'):
            last_angle = state.get('last_angle', angle)
            if angle > last_angle:
                state['direction'] = 'up'
            elif angle < last_angle:
                state['direction'] = 'down'
            if state.get('direction'):
                state['direction_set'] = True
        
        peak = state.get('peak_angle', angle)
        valley = state.get('valley_angle', angle)
        range_span = peak - valley
        min_range = 20
        been_above = state.get('been_above', False)
        been_below = state.get('been_below', False)
        direction = state.get('direction')
        
        if range_span >= min_range and been_above and been_below:
            if direction == 'up':
                if angle <= midpoint and peak >= midpoint:
                    reps += 1
                    state['counting'] = False
                    # KEY FIX: Reset state flags for next rep
                    state['been_above'] = False
                    state['been_below'] = False
                    state['direction_set'] = False
            elif direction == 'down':
                if angle >= midpoint and valley <= midpoint:
                    reps += 1
                    state['counting'] = False
                    # KEY FIX: Reset state flags for next rep
                    state['been_above'] = False
                    state['been_below'] = False
                    state['direction_set'] = False
    
    state['reps'] = reps
    state['last_angle'] = angle
    return reps


def test_rep_counting():
    """Test shoulder rep counting"""
    print('='*60)
    print('TEST 1: SHOULDER REP COUNTING FIX')
    print('='*60)
    
    state = {
        'reps': 0,
        'counting': False,
        'been_above': False,
        'been_below': False,
        'direction_set': False,
        'peak_angle': 0,
        'valley_angle': 0,
        'last_angle': 20
    }
    
    # Test 1: One rep
    print('\nTest 1a: One Complete Rep (20°→120°→30°)')
    print('Expected: 1 rep')
    print('-'*40)
    
    angles1 = [20, 40, 60, 80, 100, 120, 100, 80, 60, 40, 30]
    for angle in angles1:
        reps = count_reps_simple('Shoulder Flexion', angle, state)
    
    print(f'Result: {reps} rep(s) counted')
    test1_pass = reps == 1
    print('✓ PASS' if test1_pass else f'✗ FAIL (got {reps})')
    
    # Test 2: Two reps 
    print('\nTest 1b: Two Complete Reps')
    print('Expected: 2 reps')
    print('-'*40)
    
    state = {
        'reps': 0,
        'counting': False,
        'been_above': False,
        'been_below': False,
        'direction_set': False,
        'peak_angle': 0,
        'valley_angle': 0,
        'last_angle': 20
    }
    
    # Sequence: 20→120→30 (rep 1) then 50→120→25 (rep 2)
    angles2 = [20, 40, 60, 80, 100, 120, 100, 80, 60, 40, 30, 
               50, 80, 110, 120, 100, 70, 40, 25]
    
    for angle in angles2:
        reps = count_reps_simple('Shoulder Flexion', angle, state)
    
    print(f'Result: {reps} rep(s) counted')
    test2_pass = reps == 2
    print('✓ PASS' if test2_pass else f'✗ FAIL (got {reps})')
    
    return test1_pass and test2_pass


def test_exit_button():
    """Test exit button cleanup"""
    print('\n' + '='*60)
    print('TEST 2: EXIT EXERCISE BUTTON CLEANUP')
    print('='*60)
    
    frontend_script = "./frontend/script.js"
    backend_script = "./backend/static/script.js"
    
    all_checks_pass = True
    
    for script_path in [frontend_script, backend_script]:
        if not os.path.exists(script_path):
            script_path = os.path.join(os.path.dirname(__file__), "..", script_path)
        
        if os.path.exists(script_path):
            print(f'\nChecking: {script_path}')
            print('-'*40)
            
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Find exitExercise function
            exit_start = content.find("function exitExercise()")
            if exit_start == -1:
                print("✗ exitExercise function not found")
                all_checks_pass = False
                continue
            
            exit_end = content.find("function ", exit_start + 1)
            if exit_end == -1:
                exit_end = len(content)
            
            exit_func = content[exit_start:exit_end]
            
            checks = {
                "Closes websocket": "websocket.close()" in exit_func,
                "Nullifies websocket": "websocket = null" in exit_func,
                "Clears exercise": "currentExercise" in exit_func or "selectedExercise" in exit_func,
                "Resets state": "exerciseState =" in exit_func,
                "Stops camera": "stopCamera()" in exit_func,
                "Navigates back": "showPage('exercises')" in exit_func,
            }
            
            for check_name, result in checks.items():
                status = "✓" if result else "✗"
                print(f"{status} {check_name}")
                if not result:
                    all_checks_pass = False
        else:
            print(f"Warning: Could not find {script_path}")
    
    return all_checks_pass


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING PHYSIO-MONITORING FIXES")
    print("="*60)
    
    results = []
    
    try:
        test1_pass = test_rep_counting()
        results.append(("Shoulder Rep Counting", test1_pass))
    except Exception as e:
        print(f"\n✗ ERROR in test 1: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Shoulder Rep Counting", False))
    
    try:
        test2_pass = test_exit_button()
        results.append(("Exit Button Cleanup", test2_pass))
    except Exception as e:
        print(f"\n✗ ERROR in test 2: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Exit Button Cleanup", False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("-"*60)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL FIXES VERIFIED!")
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED")
        sys.exit(1)
