#!/usr/bin/env python3
"""Quick test of midpoint-based hysteresis rep counting"""

def count_reps_hysteresis(exercise, angle, state):
    """Test version of midpoint-based hysteresis rep counting"""
    target_min, target_max = 20, 120
    reps = state['reps']
    
    # Initialize phase
    if 'phase' not in state:
        if angle > (target_min + target_max) / 2:
            state['phase'] = 'flexed'
        else:
            state['phase'] = 'extended'
        state['last_angle'] = angle
        return reps
    
    # Check movement
    angle_delta = abs(angle - state.get('last_angle', angle))
    if angle_delta < 3:
        return reps
    
    state['last_angle'] = angle
    
    # Calculate thresholds using midpoint
    midpoint = (target_min + target_max) / 2
    extended_threshold = midpoint - (midpoint - target_min) * 0.4
    flexed_threshold = midpoint + (target_max - midpoint) * 0.4
    
    if state['phase'] == 'extended':
        if angle > flexed_threshold:
            state['phase'] = 'flexed'
    elif state['phase'] == 'flexed':
        if angle < extended_threshold:
            reps += 1
            state['phase'] = 'extended'
    
    state['reps'] = reps
    return reps

print('Testing Midpoint-Based Hysteresis Rep Counting')
print('='*50)

# Test 1: One rep
print('\nTest 1: One Complete Rep (20°→120°→30°)')
state1 = {'reps': 0}
angles1 = [20, 40, 60, 80, 100, 120, 100, 80, 60, 40, 30]
for angle in angles1:
    reps = count_reps_hysteresis('Shoulder Flexion', angle, state1)

print(f'Result: {reps} rep(s)')
print('Expected: 1 rep')
test1_pass = reps == 1
print('✓ PASS' if test1_pass else f'✗ FAIL (got {reps})')

# Test 2: Two reps
print('\nTest 2: Two Complete Reps')
state2 = {'reps': 0}
angles2 = [20, 40, 60, 80, 100, 120, 100, 80, 60, 40, 30,
           50, 80, 110, 120, 100, 70, 40, 25]
for angle in angles2:
    reps = count_reps_hysteresis('Shoulder Flexion', angle, state2)

print(f'Result: {reps} rep(s)')
print('Expected: 2 reps')
test2_pass = reps == 2
print('✓ PASS' if test2_pass else f'✗ FAIL (got {reps})')

print('\n' + '='*50)
if test1_pass and test2_pass:
    print('✓ HYSTERESIS REP COUNTING WORKS!')
else:
    print('✗ STILL NEEDS ADJUSTMENT')
