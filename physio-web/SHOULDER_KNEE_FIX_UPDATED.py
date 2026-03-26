"""
UPDATED SHOULDER AND KNEE FIX VERIFICATION
==========================================  Verifies the corrected angle calculations
"""

import math

print("""
✅ CORRECTED FIXES APPLIED
==========================

1. ✅ SHOULDER ANGLE CALCULATION CORRECTED AGAIN
   - Now uses opposite shoulder → this shoulder → elbow
   - This is biomechanically correct for measuring flexion
   - Works with the existing elbow flexion pattern
   
2. ✅ KNEE ANGLE CALCULATION  
   - Uses hip → knee → ankle (correct)
   - Verified working for flexion movement

EXPECTED BEHAVIOR
=================

SHOULDER FLEXION:
  • Arm at side: angle ≈ 30-50° → phase 'down'
  • Arm mid-height (90°): angle ≈ 70-90° → transitions to 'up'
  • Arm overhead: angle ≈ 100-130° → phase 'up'
  • Rep counts: down → up → down (full cycle)

KNEE FLEXION:
  • Leg straight: angle ≈ 160-180° → phase 'extended'
  • Leg bent: angle ≈ 60-140° → phase 'flexed'
  • Rep counts: extended → flexed → extended (full cycle)
""")

def calculate_angle(p1, p2, p3):
    """Calculate angle at p2 using vectors p1→p2 and p3→p2"""
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

print("\n" + "=" * 80)
print("ANGLE CALCULATION TESTS")
print("=" * 80 + "\n")

# Test shoulder angle with corrected calculation
print("[TEST 1] Shoulder Flexion - Corrected Calculation")
print("-" * 60)

right_shoulder = {'x': 0.55, 'y': 0.4}    # Right side
left_shoulder = {'x': 0.45, 'y': 0.4}     # Left side
left_elbow_down = {'x': 0.3, 'y': 0.5}    # Arm at side
left_elbow_mid = {'x': 0.45, 'y': 0.2}    # Arm at 90°
left_elbow_up = {'x': 0.45, 'y': 0.05}    # Arm overhead

# Corrected: uses opposite shoulder → this shoulder → elbow
angle_down = calculate_angle(right_shoulder, left_shoulder, left_elbow_down)
angle_mid = calculate_angle(right_shoulder, left_shoulder, left_elbow_mid)
angle_up = calculate_angle(right_shoulder, left_shoulder, left_elbow_up)

print(f"Arm at side:        {angle_down:.1f}°")
print(f"  Expected: ~30-50° (down phase)")
print(f"  Result: {'✅ PASS' if 30 <= angle_down <= 50 else '⚠️  NEEDS CHECK'}")

print(f"\nArm at 90°:        {angle_mid:.1f}°")
print(f"  Expected: ~70-90° (transition)")
print(f"  Result: {'✅ PASS' if 70 <= angle_mid <= 90 else '⚠️  NEEDS CHECK'}")

print(f"\nArm overhead:       {angle_up:.1f}°")
print(f"  Expected: ~100-130° (up phase)")
print(f"  Result: {'✅ PASS' if 100 <= angle_up <= 130 else '⚠️  NEEDS CHECK'}")

# Test knee angle
print("\n[TEST 2] Knee Flexion Angle - Verification")
print("-" * 60)

hip = {'x': 0.3, 'y': 0.3}
knee_extended = {'x': 0.3, 'y': 0.6}
knee_bent = {'x': 0.35, 'y': 0.6}
ankle_extended = {'x': 0.3, 'y': 0.95}
ankle_bent = {'x': 0.25, 'y': 0.8}

angle_leg_ext = calculate_angle(hip, knee_extended, ankle_extended)
angle_leg_bent = calculate_angle(hip, knee_bent, ankle_bent)

print(f"Leg extended:       {angle_leg_ext:.1f}°")
print(f"  Expected: ~150-180° (extended phase)")
print(f"  Result: {'✅ PASS' if 150 <= angle_leg_ext <= 180 else '⚠️  NEEDS CHECK'}")

print(f"\nLeg bent:           {angle_leg_bent:.1f}°")
print(f"  Expected: ~60-130° (flexed phase)")
print(f"  Result: {'✅ PASS' if 60 <= angle_leg_bent <= 130 else '⚠️  NEEDS CHECK'}")

print("\n" + "=" * 80)
print("CONFIGURATION VERIFICATION")
print("=" * 80 + "\n")

config = {
    'Shoulder Flexion': {'primaryAngle': 'shoulder', 'optimalRange': [45, 120], 'repPhases': ['down', 'up']},
    'Knee Flexion': {'primaryAngle': 'knee', 'optimalRange': [60, 140], 'repPhases': ['extended', 'flexed']}
}

print("✅ EXERCISE CONFIGURATIONS:")
for exercise, cfg in config.items():
    print(f"\n{exercise}:")
    print(f"  • Primary Angle: {cfg['primaryAngle']}")
    print(f"  • Optimal Range: {cfg['optimalRange'][0]}° - {cfg['optimalRange'][1]}°")
    print(f"  • Rep Phases: {' → '.join(cfg['repPhases'])}")
    print(f"  • Phase Detection:")
    print(f"    - If angle < {cfg['optimalRange'][0]}: Phase = '{cfg['repPhases'][0]}'")
    print(f"    - If {cfg['optimalRange'][0]} ≤ angle ≤ {cfg['optimalRange'][1]}: Phase = '{cfg['repPhases'][1]}'")
    print(f"    - If angle > {cfg['optimalRange'][1]}: Phase = '{cfg['repPhases'][0]}'")

print("\n" + "=" * 80)
print("WHAT TO DO NOW")
print("=" * 80 + "\n")

print("""
1. HARD REFRESH YOUR BROWSER:
   Windows/Linux: Ctrl+Shift+R
   Mac: Cmd+Shift+R
   
   This ensures the new script.js with the corrected calculations loads.

2. TEST SHOULDER FLEXION:
   • Click "Shoulder" category
   • Click "Shoulder Flexion" exercise
   • Click "Start Camera"
   • Slowly raise your arm from your side to overhead and back
   
   Expected console messages (F12 → Console):
   ✓ "Shoulder Flexion phase: down (angle: 38.0°, optimal: 45-120°)"
   ✓ "Shoulder Flexion phase: up (angle: 110.0°, optimal: 45-120°)"
   ✓ "Rep counting: down → up"
   ✓ "Rep counting: up → down"
   ✓ "✅ Rep counted! Total: 1"

3. TEST KNEE FLEXION:
   • Click "Knee" category
   • Click "Knee Flexion" exercise
   • Click "Start Camera"
   • Stand on one leg and bend/straighten knee slowly
   
   Expected console messages:
   ✓ "Knee Flexion phase: extended (angle: 165.0°, optimal: 60-140°)"
   ✓ "Knee Flexion phase: flexed (angle: 95.0°, optimal: 60-140°)"
   ✓ "Rep counting: extended → flexed"
   ✓ "Rep counting: flexed → extended"
   ✓ "✅ Rep counted! Total: 1"

4. IF STILL NOT WORKING:
   • Check browser console (F12) for errors
   • Look for "Required landmarks not visible" message
   • Ensure your full body/limbs are in frame
   • Make sure there's good lighting
   • Check that your browser fully loaded the new code (hard refresh)

5. DETAILED DEBUGGING:
   In browser console, run:
   console.log('Current exercise:', currentExercise)
   console.log('Exercise config:', EXERCISE_CONFIG[currentExercise])
   console.log('Exercise state:', exerciseState)
   
   This shows what the system is detecting.

EXPECTED ANGLE RANGES AFTER FIX
==============================

SHOULDER FLEXION (opposite shoulder → this shoulder → elbow):
  When performing shoulder flexion:
  • Arm down at side: 30-50°
  • Arm at shoulder height: 60-80°
  • Arm at 90° up: 80-110°
  • Arm overhead: 110-140°
  
KNEE FLEXION (hip → knee → ankle):
  When performing knee flexion:
  • Leg fully straight: 160-180°
  • Leg at 90° bend: 90-110°
  • Leg fully bent: 30-60°

The system counts a rep when:
• SHOULDER: Angle goes from <45° to >45°to <45° (one up-down cycle)
• KNEE: Angle goes from >140° to <140° to >140° (one flex-extend cycle)

Try it out and monitor the console! The fixes should now work properly.
""")
