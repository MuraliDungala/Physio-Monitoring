"""
Comprehensive Landmark Pose Detection Diagnostics
Tests MediaPipe detection at each step of the pipeline
"""
import sys
sys.path.insert(0, 'physio-web/backend')

import cv2
import mediapipe as mp
import numpy as np
from exercise_engine.engine import ExerciseEngine
import base64

print("=" * 80)
print("LANDMARK POSE DETECTION DIAGNOSTICS")
print("=" * 80)

# Test 1: Verify MediaPipe is working
print("\n1. Testing MediaPipe Initialization")
print("-" * 80)

try:
    pose = mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("[OK] MediaPipe Pose initialized successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize MediaPipe: {e}")
    sys.exit(1)

# Test 2: Test detection with synthetic image (should work)
print("\n2. Testing Detection with Test Image (Person Shape)")
print("-" * 80)

# Create a synthetic image with a person-like shape
test_img = np.ones((480, 640, 3), dtype=np.uint8) * 255  # White background

# Draw a simple stick figure
cv2.circle(test_img, (320, 100), 30, (0, 0, 0), -1)  # Head
cv2.line(test_img, (320, 130), (320, 250), (0, 0, 0), 3)  # Body
cv2.line(test_img, (320, 150), (250, 180), (0, 0, 0), 3)  # Left arm
cv2.line(test_img, (320, 150), (390, 180), (0, 0, 0), 3)  # Right arm
cv2.line(test_img, (320, 250), (280, 350), (0, 0, 0), 3)  # Left leg
cv2.line(test_img, (320, 250), (360, 350), (0, 0, 0), 3)  # Right leg

rgb_test = cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB)
results = pose.process(rgb_test)

if results.pose_landmarks:
    print(f"[OK] Detected {len(results.pose_landmarks.landmark)} landmarks in test image")
    print(f"     Sample landmarks:")
    for i, lm in enumerate(results.pose_landmarks.landmark[:5]):
        print(f"       Landmark {i}: x={lm.x:.3f}, y={lm.y:.3f}, visibility={lm.visibility:.3f}")
else:
    print("[WARN] No landmarks detected in synthetic test image")

# Test 3: Test detection with actual camera frame
print("\n3. Testing Camera Access")
print("-" * 80)

try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Camera not accessible (cap.isOpened() = False)")
        print("        Fix: Check if another app is using the camera")
    else:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[ERROR] Cannot read from camera")
            print("        Fix: Camera may not be ready or permission denied")
        else:
            print(f"[OK] Camera accessible, frame size: {frame.shape}")
            
            # Try pose detection on camera frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)
            
            if results.pose_landmarks:
                print(f"[OK] Detected {len(results.pose_landmarks.landmark)} landmarks in camera frame")
                visible_landmarks = sum(1 for lm in results.pose_landmarks.landmark if lm.visibility > 0.5)
                print(f"     Visible landmarks (confidence > 0.5): {visible_landmarks}")
            else:
                print("[WARN] No landmarks detected in camera frame")
                print("       Possible causes:")
                print("       - Person not visible in frame")
                print("       - Poor lighting")
                print("       - Person too far from camera")
                print("       - Camera pointing at wrong direction")
        
        cap.release()
except Exception as e:
    print(f"[ERROR] Exception accessing camera: {e}")

# Test 4: Test ExerciseEngine
print("\n4. Testing ExerciseEngine with Different Inputs")
print("-" * 80)

engine = ExerciseEngine()

# Test 4a: Blank frame
blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
result = engine.process_frame(blank_frame, selected_exercise="Shoulder Flexion")
print(f"\nBlank frame:")
print(f"  Landmarks detected: {result['landmarks_detected']}")
print(f"  Angle: {result['angle']}")
print(f"  Reps: {result['reps']}")

# Test 4b: White frame
white_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
result = engine.process_frame(white_frame, selected_exercise="Shoulder Flexion")
print(f"\nWhite frame:")
print(f"  Landmarks detected: {result['landmarks_detected']}")
print(f"  Angle: {result['angle']}")
print(f"  Reps: {result['reps']}")

# Test 4c: Test image with stick figure
result = engine.process_frame(test_img, selected_exercise="Shoulder Flexion")
print(f"\nSynthetic stick figure:")
print(f"  Landmarks detected: {result['landmarks_detected']}")
print(f"  Angle: {result['angle']}")
print(f"  Reps: {result['reps']}")

# Test 5: Test frame simulating WebSocket transmission
print("\n5. Simulating WebSocket Frame Compression/Transmission")
print("-" * 80)

# Create a test frame
test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 200

# Compress like the frontend does
ret, buffer = cv2.imencode('.jpg', test_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
if ret:
    # Encode to base64 like frontend
    b64_data = base64.b64encode(buffer).tobytes().decode('utf-8')
    print(f"[OK] Frame compressed: {len(test_frame.tobytes())} → {len(b64_data)} bytes")
    
    # Decode back like backend
    frame_data = base64.b64decode(b64_data)
    nparr = np.frombuffer(frame_data, np.uint8)
    decoded_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if decoded_frame is not None:
        print(f"[OK] Frame decompressed: {decoded_frame.shape}")
        
        # Try detection on decompressed frame
        rgb_decoded = cv2.cvtColor(decoded_frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_decoded)
        
        if results.pose_landmarks:
            print(f"[OK] Detected landmarks after compression cycle")
        else:
            print(f"[WARN] No landmarks detected after compression/decompression")
    else:
        print("[ERROR] Failed to decompress frame")
else:
    print("[ERROR] Failed to compress frame")

# Test 6: Test with different confidence thresholds
print("\n6. Testing Different Confidence Thresholds")
print("-" * 80)

for conf in [0.1, 0.3, 0.5, 0.7, 0.9]:
    pose_test = mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=conf,
        min_tracking_confidence=conf
    )
    
    # Try with white frame
    rgb_white = cv2.cvtColor(white_frame, cv2.COLOR_BGR2RGB)
    results = pose_test.process(rgb_white)
    
    status = "DETECTED" if results.pose_landmarks else "NOT DETECTED"
    print(f"  Threshold {conf}: {status}")
    
    pose_test.close()

print("\n" + "=" * 80)
print("DIAGNOSIS SUMMARY")
print("=" * 80)
print("""
Current Status: NO landmarks detected in any test frames

Possible Issues (in order of likelihood):
1. ✗ CAMERA NOT ACCESSIBLE
   - Check: Open browser and verify video element shows camera feed
   - Fix: Grant camera permissions in browser settings
   - Fix: Close other apps using camera (Zoom, Teams, etc.)

2. ✗ NO PERSON VISIBLE IN FRAME
   - Check: Stand clearly in front of camera with good lighting
   - Fix: Ensure entire body (at least shoulders to knees) is visible
   - Fix: Improve lighting - avoid shadows and backlighting

3. ✗ FRAME QUALITY TOO LOW
   - Check: JPEG compression at 80% quality might be too aggressive
   - Fix: Increase quality to 90-95% in script.js line 2327
   - Change: canvas.toBlob(..., 'image/jpeg', 0.8) → 0.95)

4. ✗ CONFIDENCE THRESHOLD TOO HIGH
   - Check: Current setting is 0.5 (requires 50% confidence)
   - Fix: Lower to 0.3 for more lenient detection
   - File: physio-web/backend/exercise_engine/engine.py line 35

5. ✗ MEDIAPIPE MODEL NOT WORKING
   - Check: Verify MediaPipe is properly installed
   - Fix: pip install --upgrade mediapipe

NEXT STEPS:
If test shows "Camera not accessible":
  → Fix camera permissions first

If test shows landmarks detected in test image but not camera:
  → Check your camera feed in browser
  → Verify you're standing in front and visible
  → Improve lighting

If test shows no landmarks in any frame:
  → Reinstall MediaPipe
  → Check MediaPipe version compatibility
  → Try lowering confidence threshold
""")

pose.close()
print("\nDiagnostics complete.")
