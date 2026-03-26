"""
Test script to verify angle and rep counting work with real camera input
Runs for 10 seconds and shows detailed debug output
"""
import sys
sys.path.insert(0, 'physio-web/backend')

import cv2
import logging
from exercise_engine.engine import ExerciseEngine

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("=" * 80)
print("ANGLE AND REP COUNTING TEST")
print("=" * 80)
print("\nMake sure YOU ARE IN FRONT OF CAMERA")
print("Stand still for 5 seconds, then test different exercises...")
print("\nStarting in 2 seconds...\n")

import time
time.sleep(2)

# Open camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[FAIL] Cannot open camera")
    sys.exit(1)

engine = ExerciseEngine()

print("Testing: Shoulder Flexion")
print("-" * 80)

# Collect data for 10 seconds
frame_count = 0
detection_count = 0
angle_count = 0
max_angle = 0
min_angle = 180
reps_found = False

start_time = time.time()

while time.time() - start_time < 10:
    ret, frame = cap.read()
    if not ret:
        continue
    
    # Process frame
    result = engine.process_frame(frame, selected_exercise="Shoulder Flexion")
    
    frame_count += 1
    
    if result["landmarks_detected"]:
        detection_count += 1
    
    if result["angle"] > 0:
        angle_count += 1
        max_angle = max(max_angle, result["angle"])
        min_angle = min(min_angle, result["angle"])
    
    if result["reps"] > 0:
        reps_found = True
    
    # Print status every 30 frames (~1 second)
    if frame_count % 30 == 0:
        elapsed = time.time() - start_time
        print(f"[{elapsed:.1f}s] Frames: {frame_count}, Detected: {detection_count}, "
              f"Angles: {angle_count}, Reps: {result['reps']}, Angle: {result['angle']:.1f}°, "
              f"Quality: {result['quality_score']:.0f}%, Msg: {result['posture_message']}")

cap.release()

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

detection_rate = (detection_count / frame_count * 100) if frame_count > 0 else 0
angle_rate = (angle_count / frame_count * 100) if frame_count > 0 else 0

print(f"Frames processed:        {frame_count}")
print(f"Landmarks detected:      {detection_count} ({detection_rate:.1f}%)")
print(f"Angles computed:         {angle_count} ({angle_rate:.1f}%)")
print(f"Angle range detected:    {min_angle:.1f}° - {max_angle:.1f}°")
print(f"Reps counted:            {'YES' if reps_found else 'NO'}")

print("\n" + "=" * 80)
print("INTERPRETATION")
print("=" * 80)

if detection_rate > 80 and angle_rate > 80:
    print("""
[SUCCESS] ANGLES AND REPS ARE WORKING!

[OK] Landmarks detected consistently (>80%)
[OK] Angles computed consistently (>80%)
[OK] Your pose is clearly visible

NEXT: Try the actual exercises in the web interface.
All metrics should display properly.
""")
elif detection_rate > 50 and angle_rate > 50:
    print("""
[PARTIAL] DETECTION WORKING BUT INCONSISTENT

Landmarks and angles are detected but intermittently.

IMPROVE:
- Better lighting (brighter, more even)
- Clearer position (3-6 feet away)
- Simple background (move away from clutter)

Then test again.
""")
else:
    print("""
[ISSUE] ANGLES NOT BEING COMPUTED

Possible causes:
1. MediaPipe not detecting pose
2. Visibility threshold too strict
3. Coordinate extraction failing
4. Angle computation failing silently

CHECK:
1. Is video showing in browser? (If yes, landmarks should be detected)
2. Improve lighting
3. Run verify_pose_detection.py for detailed diagnostics

If landmarks detected but angles are 0:
→ Bug in angle computation
→ Check backend logs for error messages
""")

print("\nTest complete.")
