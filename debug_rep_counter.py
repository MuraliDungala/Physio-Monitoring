"""Debug the rep counter behavior."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Physio-Monitoring'))

from src.repetition.rep_counter_improved import RepCounterImproved

counter = RepCounterImproved(min_angle=70, max_angle=140, movement_threshold=3)
angles = [160, 150, 145, 140, 120, 90, 70, 75, 160]

print("========================================")
print("DEBUG: Rep Counter State Trace")
print("min_angle=70, max_angle=140")
print("========================================\n")

for i, angle in enumerate(angles):
    print("Step {}: angle = {}".format(i+1, angle))
    print("  Before: phase={}, reps={}, has_reached_flexion={}".format(
        counter.phase, counter.reps, counter.has_reached_flexion))
    
    counter.update(angle, posture_ok=True)
    
    print("  After:  phase={}, reps={}, has_reached_flexion={}".format(
        counter.phase, counter.reps, counter.has_reached_flexion))
    print()

print("========================================")
print("Final: {} reps counted".format(counter.reps))
print("========================================")

