#!/usr/bin/env python3
"""
Check which exercises currently work correctly.
This analyzes the code configuration, not runtime detection.
"""

# Exercises supported in angle_map
angle_map_exercises = {
    "Shoulder Flexion": ["right_shoulder", "left_shoulder"],
    "Shoulder Extension": ["right_shoulder", "left_shoulder"],
    "Shoulder Abduction": ["right_shoulder", "left_shoulder"],
    "Shoulder Adduction": ["right_shoulder", "left_shoulder"],
    "Shoulder Internal Rotation": ["right_shoulder", "left_shoulder"],
    "Shoulder External Rotation": ["right_shoulder", "left_shoulder"],
    "Elbow Flexion": ["right_elbow", "left_elbow"],
    "Elbow Extension": ["right_elbow", "left_elbow"],
    "Knee Flexion": ["right_knee", "left_knee"],
    "Knee Extension": ["right_knee", "left_knee"],
    "Hip Abduction": ["right_hip", "left_hip"],
    "Hip Flexion": ["right_hip", "left_hip"],
    "Body Weight Squat": ["right_knee", "left_knee"],
    "Wall Sit": ["right_knee", "left_knee"],
    "Sumo Squat": ["right_knee", "left_knee"],
    "Partial Squat": ["right_knee", "left_knee"],
    "Squat Hold": ["right_knee", "left_knee"],
    "Ankle Dorsiflexion": ["right_ankle", "left_ankle"],
    "Ankle Plantarflexion": ["right_ankle", "left_ankle"],
    "Ankle Inversion": ["right_ankle", "left_ankle"],
    "Ankle Eversion": ["right_ankle", "left_ankle"],
    "Ankle Circles": ["right_ankle", "left_ankle"],
    "Wrist Flexion": ["right_wrist", "left_wrist"],
    "Wrist Extension": ["right_wrist", "left_wrist"],
    "Neck Flexion": ["neck_flexion"],
    "Neck Extension": ["neck_flexion"],
    "Neck Rotation": ["neck_rotation"],
    "Back Extension": ["right_shoulder", "left_shoulder"],
}

# Exercises with rep counting defined
rep_count_exercises = {
    "Shoulder Flexion": (30, 160),
    "Shoulder Extension": (10, 60),
    "Shoulder Abduction": (20, 160),
    "Shoulder Adduction": (10, 60),
    "Shoulder Internal Rotation": (40, 85),
    "Shoulder External Rotation": (35, 80),
    "Elbow Flexion": (30, 150),
    "Elbow Extension": (140, 180),
    "Knee Flexion": (40, 160),
    "Knee Extension": (140, 180),
    "Hip Abduction": (20, 80),
    "Hip Flexion": (30, 110),
    "Body Weight Squat": (60, 110),
    "Wall Sit": (80, 110),
    "Sumo Squat": (60, 110),
    "Partial Squat": (100, 130),
    "Squat Hold": (70, 100),
    "Ankle Dorsiflexion": (80, 120),
    "Ankle Plantarflexion": (100, 160),
    "Ankle Inversion": (20, 60),
    "Ankle Eversion": (0, 45),
    "Ankle Circles": (0, 360),
    "Wrist Flexion": (30, 140),
    "Wrist Extension": (30, 140),
    "Neck Flexion": (20, 60),
    "Neck Extension": (20, 60),
    "Neck Rotation": (30, 80),
    "Back Extension": (10, 60),
}

# Exercises with quality score defined
quality_score_exercises = {
    "Shoulder Flexion": (30, 170),
    "Shoulder Extension": (0, 60),
    "Shoulder Abduction": (20, 170),
    "Shoulder Adduction": (0, 60),
    "Shoulder Internal Rotation": (40, 90),
    "Shoulder External Rotation": (40, 90),
    "Elbow Flexion": (40, 140),
    "Elbow Extension": (140, 180),
    "Knee Flexion": (50, 150),
    "Knee Extension": (140, 180),
    "Hip Abduction": (20, 80),
    "Hip Flexion": (40, 110),
    "Body Weight Squat": (60, 110),
    "Wall Sit": (80, 110),
    "Sumo Squat": (60, 110),
    "Partial Squat": (100, 130),
    "Squat Hold": (70, 100),
    "Ankle Dorsiflexion": (80, 120),
    "Ankle Plantarflexion": (100, 160),
    "Ankle Inversion": (20, 60),
    "Ankle Eversion": (0, 45),
    "Ankle Circles": (0, 360),
    "Wrist Flexion": (40, 140),
    "Wrist Extension": (40, 140),
    "Neck Flexion": (80, 160),
    "Neck Extension": (80, 160),
    "Neck Rotation": (60, 120),
    "Back Extension": (20, 80),
}

# Angles computed by engine
computed_angles = {
    "right_shoulder": "via elbow-shoulder-hip",
    "left_shoulder": "via elbow-shoulder-hip",
    "right_elbow": "via shoulder-elbow-wrist",
    "left_elbow": "via shoulder-elbow-wrist",
    "right_knee": "via hip-knee-ankle",
    "left_knee": "via hip-knee-ankle",
    "right_hip": "via shoulder-hip-knee",
    "left_hip": "via shoulder-hip-knee",
    "right_ankle": "via knee-ankle-hip",
    "left_ankle": "via knee-ankle-hip",
    "neck_flexion": "via nose-head-shoulder",
    "neck_rotation": "via left_ear-nose-right_ear",
    "right_wrist": "via elbow-wrist-index",
    "left_wrist": "via elbow-wrist-index",
}

print("="*100)
print("EXERCISE SUPPORT ANALYSIS")
print("="*100)
print()

# Check which exercises have all required support
working = []
partial = []

for exercise in angle_map_exercises.keys():
    has_angle_map = exercise in angle_map_exercises
    has_rep_count = exercise in rep_count_exercises
    has_quality = exercise in quality_score_exercises
    
    # Check if required angles are computed
    angle_keys = angle_map_exercises.get(exercise, [])
    all_angles_computed = all(key in computed_angles for key in angle_keys)
    
    if has_angle_map and has_rep_count and has_quality and all_angles_computed:
        working.append(exercise)
    else:
        partial.append(exercise)

print(f"FULLY CONFIGURED EXERCISES: {len(working)}")
print("="*100)
for i, ex in enumerate(working, 1):
    print(f"{i:2d}. {ex}")

print()
print(f"PARTIALLY CONFIGURED EXERCISES: {len(partial)}")
print("="*100)
for i, ex in enumerate(partial, 1):
    print(f"{i:2d}. {ex}")

print()
print("="*100)
print("ANALYSIS")
print("="*100)
print("""
IMPORTANT DISCOVERY:
The code is configured for ALL 28+ exercises with:
- ANGLE MAPPING (which angles to track)
- REP COUNTING RANGES (when to count a rep)
- QUALITY SCORE RANGES (ideal form ranges)

However, the actual PROBLEM is:
1. Angles are being computed as 0 in _compute_angles_basic()
2. When angle = 0, the system returns "No clear joint movement detected"
3. This causes zeros for: reps, angle, quality_score

ROOT CAUSE:
The try-except blocks in angle computation are failing silently.
Possible reasons:
- Landmarks not detected (no pose data from MediaPipe)
- Coordinate extraction failing
- Angle calculation throwing exceptions caught by try-except

EXERCISES THAT TECHNICALLY SHOULD WORK:
If the angle computation was working, ALL 28 exercises would show:
- Reps counting
- Joint angles
- Quality scores  
- Posture feedback

But currently, ALL show 0 values because angles aren't being computed.
""")
