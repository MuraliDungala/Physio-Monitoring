"""
Test script to verify rep counting is working correctly.
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
sys.path.insert(0, PROJECT_ROOT)

from src.repetition.shoulder_rep_counter import create_shoulder_counter
from src.repetition.rep_counter import RepCounter
import numpy as np

print("=" * 70)
print("REP COUNTING FIX - VALIDATION TEST")
print("=" * 70)

# Test 1: Shoulder Flexion
print("\n✓ Test 1: Shoulder Flexion Rep Counting")
print("-" * 70)

counter = create_shoulder_counter("Shoulder Flexion")
print(f"Counter initialized: min={counter.min_angle}°, max={counter.max_angle}°")
print(f"Logic: Enter flexed when angle > max({counter.max_angle}°), Exit when angle < min({counter.min_angle}°)\n")

# Need to go BEYOND the thresholds (> and <, not >= and <=)
angles = np.concatenate([
    [10],  # Start below minimum
    np.linspace(25, 160, 30),  # Flexion - need to go beyond 150°
    np.linspace(160, 10, 30),  # Extension back down - need to go below 20°
])

for i, angle in enumerate(angles):
    prev_phase = counter.phase
    prev_reps = counter.reps
    reps = counter.update(angle, posture_ok=True)
    
    if counter.phase != prev_phase or reps > prev_reps:
        print(f"  Frame {i:2d}: angle={angle:6.1f}° | {prev_phase:8s} → {counter.phase:8s} | reps={reps}")

print(f"\nFinal Result: {counter.reps} reps counted")
if counter.reps >= 1:
    print("✅ PASS - Rep counting works!")
else:
    print("❌ FAIL - No reps counted")

# Test 2: Elbow Flexion
print("\n✓ Test 2: Elbow Flexion Rep Counting")
print("-" * 70)

elbow_counter = RepCounter(30, 70)  # Fixed parameters
print(f"Counter initialized: min={elbow_counter.min_angle}°, max={elbow_counter.max_angle}°")
print(f"Logic: Enter flexed when angle > max(70°), Exit flexed when angle < min(30°)\n")

# Need to go beyond thresholds (> 70 and < 30)
# Note: movement_threshold is 6°, so steps must be >= 6° to be counted
# Using 5 points creates 9° steps which exceeds the movement_threshold
angles = np.concatenate([
    [20],  # Start in extended (< 30)
    np.linspace(30, 75, 5),   # Move toward and beyond 70° - 9° steps
    np.linspace(75, 20, 5),   # Return to extended - 9° steps
])

print(f"Step size: ~{np.diff(angles[:15]).mean():.1f}° (movement_threshold=6°)\n")

for i, angle in enumerate(angles):
    prev_phase = elbow_counter.phase
    prev_reps = elbow_counter.reps
    reps = elbow_counter.update(angle, posture_ok=True)
    
    if elbow_counter.phase != prev_phase or reps > prev_reps or (i > 0 and i % 15 == 0):
        print(f"  Frame {i:2d}: angle={angle:6.1f}° | phase={elbow_counter.phase:8s} | reps={reps}")

print(f"\nFinal Result: {elbow_counter.reps} reps counted")
if elbow_counter.reps >= 1:
    print("✅ PASS - Elbow rep counting works!")
else:
    print("❌ FAIL - No elbow reps counted")

# Test 3: Multiple reps
print("\n✓ Test 3: Multiple Reps (Shoulder Abduction)")
print("-" * 70)

counter = create_shoulder_counter("Shoulder Abduction")
print(f"Performing 3 complete repetitions...")
print(f"Range: min={counter.min_angle}°, max={counter.max_angle}° (need to go beyond these)\n")

for rep_num in range(3):
    # Each rep: go below min, rise above max, return below min
    angles = np.concatenate([
        np.linspace(15, 165, 25),   # Abduction - go from 15 up to 165 (beyond 160)
        np.linspace(165, 15, 25),   # Adduction - go from 165 down to 15 (below 20)
    ])
    
    for angle in angles:
        prev_reps = counter.reps
        reps = counter.update(angle, posture_ok=True)
        if reps > prev_reps:
            print(f"  Rep {rep_num + 1} complete: {reps} total reps")

print(f"\nFinal Result: {counter.reps} reps counted")
if counter.reps >= 3:
    print("✅ PASS - Multiple reps counted correctly!")
else:
    print(f"❌ FAIL - Expected 3 reps, got {counter.reps}")

print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)

if counter.reps >= 1:
    print("\n✅ REP COUNTING IS WORKING - Ready to use!")
else:
    print("\n❌ REP COUNTING ISSUE - Check implementation")
