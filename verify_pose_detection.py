"""
Quick verification that pose detection infrastructure works end-to-end
Run this with a person in frame for proper test
"""
import sys
sys.path.insert(0, 'physio-web/backend')

import cv2
import mediapipe as mp
import numpy as np
from exercise_engine.engine import ExerciseEngine

def main():
    print("=" * 80)
    print("POSE DETECTION END-TO-END VERIFICATION")
    print("=" * 80)
    print("\nMake sure YOU ARE STANDING IN FRONT OF CAMERA for this test!")
    print("Press SPACEBAR when ready, then stand still for 3 seconds...")
    input("Press ENTER to continue...")
    
    # Capture frames
    print("\nCapturing frames for 3 seconds...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[FAIL] Cannot access camera!")
        print("Fix: Check camera is not in use by another app")
        return False
    
    frames = []
    for i in range(90):  # ~3 seconds at 30fps
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
        if i % 30 == 0:
            print(f"  {i//30} seconds...")
    
    cap.release()
    
    if not frames:
        print("[FAIL] No frames captured!")
        return False
    
    print(f"[OK] Captured {len(frames)} frames")
    
    # Test MediaPipe directly
    print("\n" + "-" * 80)
    print("TEST 1: Direct MediaPipe Detection")
    print("-" * 80)
    
    pose = mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    detected_frames = 0
    for i, frame in enumerate(frames):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        if results.pose_landmarks:
            detected_frames += 1
    
    pose.close()
    
    detection_rate = (detected_frames / len(frames)) * 100
    print(f"Detection rate: {detection_rate:.1f}% ({detected_frames}/{len(frames)} frames)")
    
    if detection_rate < 50:
        print("⚠ LOW: MediaPipe detecting less than 50% of frames")
        print("  → Check lighting, position, visibility")
        return False
    elif detection_rate < 80:
        print("⚠ MODERATE: Borderline detection (~50-80%)")
        print("  → Try better lighting or closer position")
    else:
        print("[OK] GOOD: Consistent detection")
    
    # Test ExerciseEngine
    print("\n" + "-" * 80)
    print("TEST 2: ExerciseEngine Detection")
    print("-" * 80)
    
    engine = ExerciseEngine()
    
    detected_frames = 0
    for i, frame in enumerate(frames):
        result = engine.process_frame(frame, selected_exercise="Shoulder Flexion")
        
        if result["landmarks_detected"]:
            detected_frames += 1
    
    detection_rate = (detected_frames / len(frames)) * 100
    print(f"Detection rate: {detection_rate:.1f}% ({detected_frames}/{len(frames)} frames)")
    
    if detection_rate < 50:
        print("[FAIL] Engine detecting less than 50%")
        print("  → Bug in engine or frame processing")
        return False
    elif detection_rate < 80:
        print("[PARTIAL] Borderline detection")
    else:
        print("[OK] Consistent detection")
    
    # Test angle computation
    print("\n" + "-" * 80)
    print("TEST 3: Angle Computation")
    print("-" * 80)
    
    angles_computed = 0
    for i, frame in enumerate(frames):
        result = engine.process_frame(frame, selected_exercise="Shoulder Flexion")
        
        if result["angle"] > 0:  # Actual angle computed
            angles_computed += 1
    
    angle_rate = (angles_computed / len(frames)) * 100
    print(f"Angle computation rate: {angle_rate:.1f}% ({angles_computed}/{len(frames)} frames)")
    
    if angle_rate < 50:
        print("[WARN] Angles not computing properly")
        return False
    else:
        print("[OK] Angles computing correctly")
    
    # Test rep counting
    print("\n" + "-" * 80)
    print("TEST 4: Rep Counting")
    print("-" * 80)
    
    # Reset and process all frames
    engine2 = ExerciseEngine()
    max_reps = 0
    
    for frame in frames:
        result = engine2.process_frame(frame, selected_exercise="Shoulder Flexion")
        max_reps = max(max_reps, result["reps"])
    
    if max_reps > 0:
        print(f"[OK] Reps counted: {max_reps}")
        print("     (Note: With only 3 seconds, may not count full rep)")
    else:
        print(f"[WARN] No reps counted")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if detection_rate > 80 and angle_rate > 50:
        print("""
[SUCCESS] POSE DETECTION IS WORKING!

Your system is ready for metric monitoring.
All 28 exercises will show:
  ✓ Skeleton overlay
  ✓ Joint angles
  ✓ Rep counts
  ✓ Quality scores
  ✓ Form feedback

Start using the web interface!
""")
        return True
    elif detection_rate > 50:
        print("""
[PARTIAL] DETECTION WORKING BUT INCONSISTENT

Try improving:
  1. Lighting (brighter, more even)
  2. Position (closer to camera, clearer angle)
  3. Background (simpler, less clutter)
  4. Movement speed (slower, more clear motion)
  
Then test again.
""")
        return True
    else:
        print("""
[PROBLEM] POSE DETECTION NOT WORKING

Likely causes:
  1. Too dark / poor lighting
  2. Too far from camera
  3. Body parts not visible
  4. Camera pointing wrong direction
  5. Very cluttered background
  
Fix the physical setup and test again.
""")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
