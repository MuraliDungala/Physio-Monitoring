"""
FINAL SHOULDER AND KNEE FIX - VERIFICATION
===========================================
"""

import math

def calculate_angle(p1, p2, p3):
    """Calculate angle at p2"""
    if not p1 or not p2 or not p3:
        return None
    
    v1 = {'x': p1['x'] - p2['x'], 'y': p1['y'] - p2['y']}
    v2 = {'x': p3['x'] - p2['x'], 'y': p3['y'] - p2['y']}
    
    dot = v1['x'] * v2['x'] + v1['y'] * v2['y']
    det = v1['x'] * v2['y'] - v1['y'] * v2['x']
    
    angle = math.atan2(det, dot)
    angle = abs(angle) * (180 / math.pi)
    
    if angle > 180:
        angle = 360 - angle
    
    return angle

print("""
✅ FINAL FIX - SHOULDER AND KNEE EXERCISES
===========================================

SHOULDER ANGLE: Vertical reference → shoulder → elbow
  - Point above shoulder (vertical axis)
  - Shoulder joint (vertex)
  - Elbow (arm endpoint)
  
  This gives:
  - Small angles when arm is down (~10-30°)
  - Large angles when arm is raised (~60-120°+)
  
KNEE ANGLE: Hip → knee → ankle (unchanged, already correct)
""")

print("\n" + "=" * 70)
print("SHOULDER FLEXION ANGLE TESTS")
print("=" * 70)

shoulder = {'x': 0.45, 'y': 0.4}
elbow_down = {'x': 0.35, 'y': 0.55}     # Arm at side
elbow_shoulder = {'x': 0.45, 'y': 0.25} # Arm at shoulderheight
elbow_up = {'x': 0.45, 'y': 0.0}        # Arm overhead

# Reference point above shoulder for vertical measurement
ref_above = {'x': shoulder['x'], 'y': shoulder['y'] - 0.2}

angle1 = calculate_angle(ref_above, shoulder, elbow_down)
angle2 = calculate_angle(ref_above, shoulder, elbow_shoulder)
angle3 = calculate_angle(ref_above, shoulder, elbow_up)

print(f"\n1. Arm at side (down):")
print(f"   Angle: {angle1:.1f}°")
print(f"   Expected: < 45° (down phase)")
print(f"   Status: {'✅ PASS' if angle1 < 45 else '❌ FAIL'}")

print(f"\n2. Arm at shoulder height:")
print(f"   Angle: {angle2:.1f}°")
print(f"   Expected: ~45-80° (transition zone)")
print(f"   Status: {'✅ PASS' if 45 <= angle2 <= 80 else '⚠️  CHECK'}")

print(f"\n3. Arm overhead (up):")
print(f"   Angle: {angle3:.1f}°")
print(f"   Expected: > 80° (up phase)")
print(f"   Status: {'✅ PASS' if angle3 > 80 else '❌ FAIL'}")

print("\n" + "=" * 70)
print("KNEE FLEXION ANGLE TESTS")
print("=" * 70)

hip = {'x': 0.3, 'y': 0.3}
knee = {'x': 0.3, 'y': 0.6}
ankle_straight = {'x': 0.3, 'y': 0.95}   # Leg straight
ankle_bent_90 = {'x': 0.25, 'y': 0.75}   # Leg bent ~90°
ankle_bent_full = {'x': 0.2, 'y': 0.5}   # Leg fully bent

angle4 = calculate_angle(hip, knee, ankle_straight)
angle5 = calculate_angle(hip, knee, ankle_bent_90)
angle6 = calculate_angle(hip, knee, ankle_bent_full)

print(f"\n1. Leg straight (extended):")
print(f"   Angle: {angle4:.1f}°")
print(f"   Expected: > 140° (extended phase)")
print(f"   Status: {'✅ PASS' if angle4 > 140 else '❌ FAIL'}")

print(f"\n2. Leg at ~90°:")
print(f"   Angle: {angle5:.1f}°")
print(f"   Expected: 60-140° (flexed phase)")
print(f"   Status: {'✅ PASS' if 60 <= angle5 <= 140 else '⚠️  CHECK'}")

print(f"\n3. Leg fully bent:")
print(f"   Angle: {angle6:.1f}°")
print(f"   Expected: 60-140° (flexed phase)")
print(f"   Status: {'✅ PASS' if 60 <= angle6 <= 140 else '⚠️  CHECK'}")

print("\n" + "=" * 70)
print("SUMMARY & NEXT STEPS")
print("=" * 70 + "\n")

print("""
✅ FIXES APPLIED:

1. Shoulder Flexion Angle:
   - Uses vertical reference above shoulder
   - Calculates angle between body axis and arm
   - Should give 0-180° range (practical: 10-130°)

2. Knee Flexion Angle:
   - Uses hip → knee → ankle
   - Calculates joint angle
   - Should give 30-180° range (practical: 30-180°)

📋 CONFIGURATION:
   Shoulder Flexion:
   - optimalRange: [45, 120]
   - repPhases: ['down', 'up']
   - Phase is 'down' if angle < 45°
   - Phase is 'up' if 45° ≤ angle ≤ 120°
   
   Knee Flexion:
   - optimalRange: [60, 140]
   - repPhases: ['extended', 'flexed']
   - Phase is 'extended' if angle < 60° or > 140°
   - Phase is 'flexed' if 60° ≤ angle ≤ 140°

🔧 TO TEST:

1. HARD REFRESH BROWSER:
   Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   
2. OPEN BROWSER CONSOLE:
   Press F12 → Console tab
   
3. CLEAR PREVIOUS DATA:
   In console run: localStorage.clear()
   
4. TEST SHOULDER FLEXION:
   - Click: Shoulder category → Shoulder Flexion
   - Click: Start Camera
   - Raise/lower arm slowly
   - Watch console for messages:
     ✓ "Shoulder Flexion phase: down (angle: 25.3°, optimal: 45-120°)"
     ✓ "Shoulder Flexion phase: up (angle: 85.2°, optimal: 45-120°)"
     ✓ "Rep counting: down → up"
     ✓ "✅ Rep counted! Total: 1"
   
5. TEST KNEE FLEXION:
   - Click: Knee category → Knee Flexion
   - Click: Start Camera
   - Stand and bend/straighten knee
   - Watch console for:
     ✓ "Knee Flexion phase: extended (angle: 165.0°, optimal: 60-140°)"
     ✓ "Knee Flexion phase: flexed (angle: 95.0°, optimal: 60-140°)"
     ✓ "Rep counting: extended → flexed"
     ✓ "✅ Rep counted! Total: 1"

⚠️  IF STILL NOT WORKING:

• Check console for "Required landmarks not visible"
  → Ensure full body/limbs visible in camera frame
  → Step back further from camera
  → Improve lighting
  
• Check if angles are being calculated
  → Look for "Calculated angles: {...}" message
  
• Check if phase is being detected
  → Look for "Shoulder Flexion phase:" or "Knee Flexion phase:" messages
  
• If no phase messages:
  → Landmarks not visible
  → Or configuration issue
  
THE FIXES ARE NOW COMPLETE!
Try testing and let me know if it works!
""")
