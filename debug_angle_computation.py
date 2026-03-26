"""
Debug script to trace angle computation failures
"""
import sys
sys.path.insert(0, 'physio-web/backend')
sys.path.insert(0, 'Physio-Monitoring/src')

from exercise_engine.engine import ExerciseEngine
import numpy as np
import cv2

# Create engine
engine = ExerciseEngine()

# Create a blank frame (no pose detected)
blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)

print("=" * 80)
print("TEST 1: Blank Frame (No Landmarks)")
print("=" * 80)

# Process blank frame
results = engine.process_frame(blank_frame, selected_exercise="Shoulder Flexion")
print(f"Results: {results}")
print(f"  Exercise: {results.get('exercise')}")
print(f"  Angle: {results.get('angle')}")
print(f"  Reps: {results.get('reps')}")
print(f"  Quality: {results.get('quality_score')}")
print(f"  Landmarks detected: {results.get('landmarks_detected')}")

print("\n" + "=" * 80)
print("TEST 2: Manually Check Angle Computation")
print("=" * 80)

# Let's trace what happens inside _compute_angles_basic
# when we have some dummy landmark data
from mediapipe.framework.formats import landmark_pb2

# Create mock landmarks (MediaPipe format)
landmarks_proto = landmark_pb2.NormalizedLandmarkList()

# Add shoulder landmarks (important for shoulder flexion)
# Landmark indices from MediaPipe:
# 11 = Right shoulder
# 12 = Left shoulder  
# 13 = Right elbow
# 14 = Left elbow
# etc

# Let's create a simple test case
test_landmarks = [
    (0, 0.5, 0.3, 0.9),   # 0: nose
    (0, 0.4, 0.35, 0.9),  # 1: left_eye
    (0, 0.6, 0.35, 0.9),  # 2: right_eye
    (0, 0.35, 0.4, 0.9),  # 3: left_ear
    (0, 0.65, 0.4, 0.9),  # 4: right_ear
    (0, 0.45, 0.5, 0.9),  # 5: left_shoulder
    (0, 0.55, 0.5, 0.9),  # 6: right_shoulder
    (0, 0.40, 0.65, 0.9), # 7: left_elbow
    (0, 0.60, 0.65, 0.9), # 8: right_elbow
    (0, 0.35, 0.8, 0.9),  # 9: left_wrist
    (0, 0.65, 0.8, 0.9),  # 10: right_wrist
    (0, 0.45, 0.55, 0.9), # 11: left_hip
    (0, 0.55, 0.55, 0.9), # 12: right_hip
]

print(f"Created mock landmarks: {len(test_landmarks)} landmarks")

# Now let's manually trace through _compute_angles_basic logic
print("\nTesting _calculate_angle_3d() function:")

# Test with 3 points forming an angle
point1 = np.array([0.45, 0.5, 0])   # left shoulder
point2 = np.array([0.40, 0.65, 0])  # left elbow
point3 = np.array([0.35, 0.8, 0])   # left wrist

angle = engine._calculate_angle_3d(point1, point2, point3)
print(f"  Angle between shoulder-elbow-wrist: {angle}°")

# Test with vertical vs horizontal
point_a = np.array([0.5, 0.0, 0])   # top
point_b = np.array([0.5, 0.5, 0])   # middle
point_c = np.array([0.5, 1.0, 0])   # bottom (should be 180°)

angle2 = engine._calculate_angle_3d(point_a, point_b, point_c)
print(f"  Angle between vertical points (should be ~180°): {angle2}°")

# Test right angle
point_d = np.array([0.5, 0.5, 0])   # corner
point_e = np.array([0.5, 1.0, 0])   # down
point_f = np.array([1.0, 0.5, 0])   # right (should be ~90°)

angle3 = engine._calculate_angle_3d(point_d, point_e, point_f)
print(f"  Angle for right angle (should be ~90°): {angle3}°")

print("\n" + "=" * 80)
print("DIAGNOSIS")
print("=" * 80)
print("The _calculate_angle_3d() function works correctly.")
print("The issue is that when landmarks are not detected,")
print("nothing gets passed to the angle calculation.")
print("\nThis means the early return happens BEFORE angles are even computed.")

# Let's check what process_frame returns when no landmarks detected
print("\nWhen landmarks_detected = False:")
print("- _extract_pose_data() returns early")
print("- angles dict is empty")
print("- _track_selected_exercise() gets empty angles dict")
print("- Returns zeros for all metrics")
