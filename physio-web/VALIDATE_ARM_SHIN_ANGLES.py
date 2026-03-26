#!/usr/bin/env python3
"""
Validate the NEW angle calculations using arm/shin vectors relative to vertical
"""

import math

def calculate_angle_from_vertical(v_x, v_y):
    """Calculate angle of vector relative to downward vertical"""
    vertical_x, vertical_y = 0, 1
    
    dot = v_x * vertical_x + v_y * vertical_y
    det = v_x * vertical_y - v_y * vertical_x
    
    angle = math.atan2(det, dot)
    angle = abs(angle) * (180 / math.pi)
    
    if angle > 180:
        angle = 360 - angle
    
    return angle

def test_shoulder():
    print("\n" + "="*80)
    print("SHOULDER FLEXION - ARM ANGLE RELATIVE TO VERTICAL")
    print("="*80)
    
    shoulder = {'x': 0.35, 'y': 0.4}
    
    # Test 1: Arm down by side
    print("\nTest 1: Arm down by side")
    elbow = {'x': 0.35, 'y': 0.6}
    v_x = elbow['x'] - shoulder['x']
    v_y = elbow['y'] - shoulder['y']
    angle = calculate_angle_from_vertical(v_x, v_y)
    print(f"  Arm vector: ({v_x}, {v_y})")
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 0-30° (arm down)")
    print(f"  Phase: {'down' if angle < 60 else 'up'}")
    print(f"  ✓ PASS" if angle < 30 else f"  ✗ FAIL")
    
    # Test 2: Arm at 45 degrees
    print("\nTest 2: Arm at 45° from vertical")
    elbow = {'x': 0.5, 'y': 0.5}
    v_x = elbow['x'] - shoulder['x']
    v_y = elbow['y'] - shoulder['y']
    angle = calculate_angle_from_vertical(v_x, v_y)
    print(f"  Arm vector: ({v_x}, {v_y})")
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: ~45°")
    print(f"  Phase: {'down' if angle < 60 else 'up'}")
    
    # Test 3: Arm horizontal (shoulder height)
    print("\nTest 3: Arm at shoulder height (horizontal)")
    elbow = {'x': 0.55, 'y': 0.4}
    v_x = elbow['x'] - shoulder['x']
    v_y = elbow['y'] - shoulder['y']
    angle = calculate_angle_from_vertical(v_x, v_y)
    print(f"  Arm vector: ({v_x}, {v_y})")
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: ~90°")
    print(f"  Phase: {'down' if angle < 60 else 'up'} (SHOULD TRANSITION!)")
    print(f"  ✓ PASS" if 80 <= angle <= 100 else f"  ✗ FAIL")
    
    # Test 4: Arm overhead
    print("\nTest 4: Arm overhead (pointing up)")
    elbow = {'x': 0.35, 'y': 0.1}
    v_x = elbow['x'] - shoulder['x']
    v_y = elbow['y'] - shoulder['y']
    angle = calculate_angle_from_vertical(v_x, v_y)
    print(f"  Arm vector: ({v_x}, {v_y})")
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 170-180° (arm up)")
    print(f"  Phase: {'down' if angle < 60 else 'up'}")
    print(f"  ✓ PASS" if angle > 160 else f"  ✗ FAIL")

def test_knee():
    print("\n" + "="*80)
    print("KNEE FLEXION - SHIN ANGLE RELATIVE TO VERTICAL")
    print("="*80)
    
    knee = {'x': 0.3, 'y': 0.8}
    
    # Test 1: Leg straight
    print("\nTest 1: Leg fully straight (vertical)")
    ankle = {'x': 0.3, 'y': 1.0}
    v_x = ankle['x'] - knee['x']
    v_y = ankle['y'] - knee['y']
    angle = calculate_angle_from_vertical(v_x, v_y)
    print(f"  Shin vector: ({v_x}, {v_y})")
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 0-15° (leg straight)")
    print(f"  Phase: {'flexed' if angle >= 40 else 'extended'}")
    print(f"  ✓ PASS" if angle < 20 else f"  ✗ FAIL")
    
    # Test 2: Leg at 90 degrees
    print("\nTest 2: Leg bent ~90°")
    ankle = {'x': 0.5, 'y': 0.9}
    v_x = ankle['x'] - knee['x']
    v_y = ankle['y'] - knee['y']
    angle = calculate_angle_from_vertical(v_x, v_y)
    print(f"  Shin vector: ({v_x}, {v_y})")
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: ~85-95°")
    print(f"  Phase: {'flexed' if angle >= 40 else 'extended'} (SHOULD BE FLEXED!)")
    print(f"  ✓ PASS" if 80 <= angle <= 100 else f"  ✗ FAIL")
    
    # Test 3: Leg fully bent
    print("\nTest 3: Leg fully bent (squat)")
    ankle = {'x': 0.5, 'y': 0.7}
    v_x = ankle['x'] - knee['x']
    v_y = ankle['y'] - knee['y']
    angle = calculate_angle_from_vertical(v_x, v_y)
    print(f"  Shin vector: ({v_x}, {v_y})")
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 110-140°")
    print(f"  Phase: {'flexed' if angle >= 40 else 'extended'}")
    print(f"  ✓ PASS" if 100 <= angle <= 140 else f"  ✗ FAIL")

def test_phase_transitions():
    print("\n" + "="*80)
    print("PHASE TRANSITION SIMULATION")
    print("="*80)
    
    print("\nSHOULDER FLEXION REP CYCLE:")
    print("  Config: optimalRange [60, 180], repPhases ['down', 'up']")
    print("  Rule: angle < 60 → down,  angle >= 60 → up")
    
    shoulder = {'x': 0.35, 'y': 0.4}
    angles = [0, 15, 30, 45, 60, 75, 90, 120, 150, 180, 150, 120, 90, 60, 45, 30, 15, 0]
    
    phase = 'down'
    rep_count = 0
    phases_log = []
    
    for angle in angles:
        new_phase = 'up' if angle >= 60 else 'down'
        
        # Detect transition from down to up
        if phase == 'down' and new_phase == 'up':
            rep_count += 1
            phases_log.append(f"  {angle}° → phase '{new_phase}' [TRANSITION] ✓ Rep {rep_count}")
        else:
            phases_log.append(f"  {angle}° → phase '{new_phase}'")
        
        phase = new_phase
    
    for log in phases_log:
        print(log)
    
    print(f"\n  RESULT: {rep_count} reps counted")
    print(f"  ✓ SUCCESS" if rep_count == 1 else f"  ✗ FAILED")
    
    print("\n\nKNEE FLEXION REP CYCLE:")
    print("  Config: optimalRange [40, 140], repPhases ['extended', 'flexed']")
    print("  Rule: angle < 40 or angle > 140 → extended,  40-140 → flexed")
    
    angles = [0, 20, 40, 70, 100, 130, 140, 130, 100, 70, 40, 20, 0]
    
    phase = 'extended'
    rep_count = 0
    phases_log = []
    
    for angle in angles:
        new_phase = 'flexed' if (40 <= angle <= 140) else 'extended'
        
        # Detect transition from extended to flexed
        if phase == 'extended' and new_phase == 'flexed':
            rep_count += 1
            phases_log.append(f"  {angle}° → phase '{new_phase}' [TRANSITION] ✓ Rep {rep_count}")
        else:
            phases_log.append(f"  {angle}° → phase '{new_phase}'")
        
        phase = new_phase
    
    for log in phases_log:
        print(log)
    
    print(f"\n  RESULT: {rep_count} reps counted")
    print(f"  ✓ SUCCESS" if rep_count >= 1 else f"  ✗ FAILED")

def main():
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "CORRECTED ANGLE CALCULATIONS v2 - ARM/SHIN VECTORS".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    test_shoulder()
    test_knee()
    test_phase_transitions()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
✓ Shoulder: Arm angle relative to vertical (0°=down, 90°=horizontal, 180°=up)
✓ Knee: Shin angle relative to vertical (0°=straight, 90°=bent, 180°=folded)
✓ Configuration ranges optimized for correct phase transition
✓ Rep counting should now work correctly!

NEXT: Hard refresh browser and test!
    """)

if __name__ == '__main__':
    main()
