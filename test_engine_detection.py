"""
Direct test: Process actual camera frame through ExerciseEngine
"""
import sys
sys.path.insert(0, 'physio-web/backend')

import cv2
import mediapipe as mp
import numpy as np
from exercise_engine.engine import ExerciseEngine

print("=" * 80)
print("CAMERA FRAME TEST")
print("=" * 80)

# Get camera frame
print("\nCapturing camera frame...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[ERROR] Cannot open camera")
    sys.exit(1)

ret, frame = cap.read()
cap.release()

if not ret or frame is None:
    print("[ERROR] Cannot read frame from camera")
    sys.exit(1)

print(f"[OK] Camera frame captured: {frame.shape}")

# Test 1: Direct MediaPipe
print("\n" + "=" * 80)
print("TEST 1: Direct MediaPipe Detection on Camera Frame")
print("=" * 80)

pose = mp.solutions.pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
results = pose.process(rgb_frame)

if results.pose_landmarks:
    landmarks_list = results.pose_landmarks.landmark
    print(f"[OK] MediaPipe detected {len(landmarks_list)} landmarks")
    
    visible = sum(1 for lm in landmarks_list if lm.visibility > 0.5)
    print(f"     Visible landmarks (>0.5): {visible}")
    
    # Show some landmarks
    print("\n     First 5 landmarks:")
    for i in range(min(5, len(landmarks_list))):
        lm = landmarks_list[i]
        print(f"       [{i}] x={lm.x:.3f}, y={lm.y:.3f}, z={lm.z:.3f}, visibility={lm.visibility:.3f}")
else:
    print("[NO] No landmarks detected")

pose.close()

# Test 2: ExerciseEngine
print("\n" + "=" * 80)
print("TEST 2: ExerciseEngine on Same Camera Frame")
print("=" * 80)

engine = ExerciseEngine()

# Test with no exercise selected (auto-detect)
print("\nAuto-detection mode (no exercise selected):")
result = engine.process_frame(frame, selected_exercise=None)
print(f"  Landmarks detected: {result['landmarks_detected']}")
print(f"  Exercise: {result['exercise']}")
print(f"  Angle: {result['angle']}")
print(f"  Reps: {result['reps']}")

# Test with exercise selected
print("\nExercise-specific mode (Shoulder Flexion):")
result = engine.process_frame(frame, selected_exercise="Shoulder Flexion")
print(f"  Landmarks detected: {result['landmarks_detected']}")
print(f"  Exercise: {result['exercise']}")
print(f"  Angle: {result['angle']}")
print(f"  Reps: {result['reps']}")
print(f"  Quality: {result['quality_score']}")

# Test 3: Check engine's pose object
print("\n" + "=" * 80)
print("TEST 3: Debugging Engine's Pose State")
print("=" * 80)

print(f"Engine pose object: {engine.pose}")
print(f"Engine pose type: {type(engine.pose)}")

# Manually process frame using engine's pose
if engine.pose:
    print("\nManually processing with engine's pose object:")
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = engine.pose.process(rgb_frame)
    
    if results.pose_landmarks:
        print(f"[OK] Engine's pose detected {len(results.pose_landmarks.landmark)} landmarks")
    else:
        print(f"[NO] Engine's pose detected NO landmarks")
else:
    print("[ERROR] Engine's pose is None")

print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)

if result['landmarks_detected']:
    print("""
[OK] POSE DETECTION IS WORKING!

The system is correctly:
1. Capturing camera frames
2. Detecting 33 body landmarks
3. Computing angles
4. Tracking exercises

Next step: Check if metrics display properly in web interface
""")
else:
    print("""
[ISSUE] Landmarks detected by direct MediaPipe but NOT by ExerciseEngine

Possible causes:
1. ExerciseEngine's pose object configuration different from test pose
2. Frame format issue (color space, dtype)
3. Engine's confidence thresholds filtering landmarks
4. Bug in results.pose_landmarks check

Debug info:
- Check if engine.pose is initialized
- Check if results.pose_landmarks is None
- Check model_complexity difference
- Check confidence threshold settings
""")
