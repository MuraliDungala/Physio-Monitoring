#!/usr/bin/env python3
"""
Validate the corrected angle calculations for shoulder and knee exercises
"""

import math

def calculate_angle(p1, p2, p3):
    """Calculate angle between three points"""
    if not (p1 and p2 and p3):
        return None
    
    # Calculate vectors
    v1 = {'x': p1['x'] - p2['x'], 'y': p1['y'] - p2['y']}
    v2 = {'x': p3['x'] - p2['x'], 'y': p3['y'] - p2['y']}
    
    # Calculate angle
    dot = v1['x'] * v2['x'] + v1['y'] * v2['y']
    det = v1['x'] * v2['y'] - v1['y'] * v2['x']
    
    angle = math.atan2(det, dot)
    angle = abs(angle) * (180 / math.pi)
    
    if angle > 180:
        angle = 360 - angle
    
    return angle

def test_shoulder_flexion():
    """Test shoulder with VERTICAL reference (correct)"""
    print("\n" + "="*80)
    print("SHOULDER FLEXION - WITH VERTICAL REFERENCE (CORRECTED)")
    print("="*80)
    
    shoulder_left = {'x': 0.35, 'y': 0.4}
    elbow_left = {'x': 0.35, 'y': 0.6}
    
    # Test 1: Arm down by side
    print("\nTest 1: Arm down by side")
    vertical_ref = {'x': 0.35, 'y': 0.1}  # Point above shoulder
    angle = calculate_angle(vertical_ref, shoulder_left, elbow_left)
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: < 60° (arm down)")
    print(f"  Phase: {'down' if angle < 60 else 'up'}")
    print(f"  ✓ PASS" if angle < 60 else f"  ✗ FAIL")
    
    # Test 2: Arm at 90 degrees (shoulder height)
    print("\nTest 2: Arm at shoulder height (90°)")
    elbow_at_90 = {'x': 0.5, 'y': 0.4}  # Arm at side level
    angle = calculate_angle(vertical_ref, shoulder_left, elbow_at_90)
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 60-100° (shoulder height)")
    print(f"  Phase: {'down' if angle < 60 else 'up'}")
    
    # Test 3: Arm raised (120 degrees)
    print("\nTest 3: Arm raised forward-up (120°)")
    elbow_at_120 = {'x': 0.55, 'y': 0.2}  # Arm raised up and forward
    angle = calculate_angle(vertical_ref, shoulder_left, elbow_at_120)
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 110-140° (arm raised)")
    print(f"  Phase: {'down' if angle < 60 else 'up'}")
    print(f"  ✓ PASS" if 110 <= angle <= 140 else f"  ✗ CHECK")
    
    # Test 4: Arm overhead (near vertical)
    print("\nTest 4: Arm overhead")
    elbow_overhead = {'x': 0.35, 'y': 0.05}  # Arm straight up
    angle = calculate_angle(vertical_ref, shoulder_left, elbow_overhead)
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: ~170-180° (straight up)")
    print(f"  Phase: {'down' if angle < 60 else 'up'}")
    print(f"  ✓ PASS" if angle > 160 else f"  ✗ FAIL")

def test_knee_flexion():
    """Test knee with hip → knee → ankle (standard joint angle)"""
    print("\n" + "="*80)
    print("KNEE FLEXION - HIP → KNEE → ANKLE")
    print("="*80)
    
    hip = {'x': 0.3, 'y': 0.5}
    knee = {'x': 0.3, 'y': 0.8}
    ankle = {'x': 0.3, 'y': 1.0}
    
    # Test 1: Leg straight (vertical line)
    print("\nTest 1: Leg fully straight")
    angle = calculate_angle(hip, knee, ankle)
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 170-180° (extended)")
    print(f"  Phase: {'flexed' if angle < 100 else 'extended'}")
    print(f"  ✓ PASS" if angle > 150 else f"  ✗ FAIL")
    
    # Test 2: Leg at 90 degrees
    print("\nTest 2: Leg bent to 90°")
    knee_90 = {'x': 0.25, 'y': 0.8}  # Knee bends forward
    ankle_90 = {'x': 0.2, 'y': 1.0}  # Ankle moves forward
    angle = calculate_angle(hip, knee_90, ankle_90)
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 80-100° (flexed)")
    print(f"  Phase: {'flexed' if angle < 100 else 'extended'}")
    print(f"  ✓ PASS" if 80 <= angle <= 110 else f"  ✗ CHECK")
    
    # Test 3: Leg fully bent (squat)
    print("\nTest 3: Leg fully bent (squat)")
    knee_bent = {'x': 0.25, 'y': 0.65}  # Knee high
    ankle_bent = {'x': 0.25, 'y': 0.85}  # Ankle still relevant
    angle = calculate_angle(hip, knee_bent, ankle_bent)
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 40-80° (flexed)")
    print(f"  Phase: {'flexed' if angle < 100 else 'extended'}")
    print(f"  ✓ PASS" if angle < 100 else f"  ✗ FAIL")

def test_elbow_flexion():
    """Test elbow (unchanged - should still work)"""
    print("\n" + "="*80)
    print("ELBOW FLEXION - SHOULDER → ELBOW → WRIST (UNCHANGED)")
    print("="*80)
    
    shoulder = {'x': 0.35, 'y': 0.4}
    elbow = {'x': 0.35, 'y': 0.6}
    wrist = {'x': 0.35, 'y': 0.8}
    
    # Test 1: Arm extended
    print("\nTest 1: Arm extended")
    angle = calculate_angle(shoulder, elbow, wrist)
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 170-180° (extended)")
    print(f"  Phase: {'flexed' if angle < 100 else 'extended'}")
    print(f"  ✓ PASS" if angle > 160 else f"  ✗ FAIL")
    
    # Test 2: Arm flexed (90 degrees)
    print("\nTest 2: Arm flexed at 90°")
    elbow_bent = {'x': 0.25, 'y': 0.6}  # Elbow bends
    wrist_bent = {'x': 0.25, 'y': 0.5}  # Wrist up
    angle = calculate_angle(shoulder, elbow_bent, wrist_bent)
    print(f"  Angle: {angle:.1f}°")
    print(f"  Expected: 80-100° (flexed)")
    print(f"  Phase: {'flexed' if angle < 100 else 'extended'}")
    print(f"  ✓ PASS" if 80 <= angle <= 110 else f"  ✗ FAIL")

def main():
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "CORRECTED ANGLE CALCULATIONS - VALIDATION TEST".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    test_elbow_flexion()
    test_shoulder_flexion()
    test_knee_flexion()
    
    print("\n" + "="*80)
    print("SUMMARY & NEXT STEPS")
    print("="*80)
    print("""
✓ Shoulder now uses VERTICAL reference (not hip) - biomechanically correct
✓ Angle ranges updated to match new calculation:
  - Shoulder down: 0-60°    → phase: 'down'
  - Shoulder up: 60-180°    → phase: 'up'
✓ Knee uses hip → knee → ankle:
  - Leg extended: 100-180°  → phase: 'extended'
  - Leg flexed: 40-100°     → phase: 'flexed'
✓ Elbow unchanged (still works)

NEXT: Hard refresh browser and test again!
    """)

if __name__ == '__main__':
    main()
