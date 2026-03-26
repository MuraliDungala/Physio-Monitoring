#!/usr/bin/env python3
"""
Debug hip exercise rep counting issues
"""
import sys
from pathlib import Path
import cv2
import mediapipe as mp

sys.path.insert(0, str(Path(__file__).parent / "physio-web" / "backend"))

from exercise_engine.engine import ExerciseEngine

def debug_hip_exercise():
    """Debug hip exercise rep counting in real-time"""
    
    print("=" * 70)
    print("HIP EXERCISE REP COUNTING DEBUG")
    print("=" * 70)
    print("\nInstructions:")
    print("1. Position yourself in front of the webcam")
    print("2. Perform hip abduction (move leg to the side)")
    print("3. Watch the debug output to see angle, motion, and rep counts")
    print("4. Press 'q' to quit\n")
    
    engine = ExerciseEngine()
    
    # MediaPipe setup
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True
    )
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam")
        return
    
    frame_count = 0
    angles_history = []
    motion_history = []
    reps_count = 0
    
    print("\nFrame | Angle | Motion | Phase | Reps | Status")
    print("-" * 70)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        if results.pose_landmarks:
            # Process with engine
            result = engine.process_frame(frame, selected_exercise="Hip Abduction")
            
            if result:
                angle = result.get("angle", 0)
                reps = result.get("reps", 0)
                message = result.get("posture_message", "")
                
                # Get state for debugging
                state = engine.state_manager.get_state("Hip Abduction")
                phase = state.get("phase", "unknown")
                
                # Get motion value
                coords, angles, motion = engine._extract_pose_data(results.pose_landmarks)
                motion_val = motion.get("hip_abduction", 0)
                
                angles_history.append(angle)
                motion_history.append(motion_val)
                
                # Rep change indicator
                rep_indicator = " ✅ REP!" if reps > reps_count else ""
                reps_count = reps
                
                # Debug output
                status = "OK"
                if motion_val < 2.0:
                    status = "LOW_MOTION"
                
                print(f"{frame_count:>5} | {angle:>6.1f}° | {motion_val:>6.2f} | {phase:>5} | {reps:>4} | {status}{rep_indicator}")
                
                # Display on frame
                h, w = frame.shape[:2]
                cv2.putText(frame, f"Angle: {angle:.1f}°", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Motion: {motion_val:.2f}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Reps: {reps}", (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Phase: {phase}", (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, message, (10, 190), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imshow("Hip Exercise Debug", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    pose.close()
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total frames: {frame_count}")
    print(f"Final reps counted: {reps_count}")
    
    if angles_history:
        print(f"\nAngle Statistics:")
        print(f"  Min: {min(angles_history):.1f}°")
        print(f"  Max: {max(angles_history):.1f}°")
        print(f"  Mean: {sum(angles_history)/len(angles_history):.1f}°")
        print(f"  Range: {max(angles_history) - min(angles_history):.1f}°")
    
    if motion_history:
        print(f"\nMotion Statistics:")
        print(f"  Min: {min(motion_history):.2f}°/frame")
        print(f"  Max: {max(motion_history):.2f}°/frame")
        print(f"  Mean: {sum(motion_history)/len(motion_history):.2f}°/frame")
        print(f"  Frames with motion >= 2.0: {sum(1 for m in motion_history if m >= 2.0)}/{len(motion_history)}")
    
    print("\n💡 Recommendations:")
    if min(angles_history) > 30:
        print("  - Starting angle is too high (>30°). Need to start from standing position (0-10°)")
    if max(angles_history) < 40:
        print("  - Maximum angle is too low (<40°). Abduction range needs to be wider")
    if sum(1 for m in motion_history if m >= 2.0) < len(motion_history) * 0.5:
        print("  - Motion detection is failing. May need to reduce motion threshold")
    
    print("=" * 70)

if __name__ == "__main__":
    try:
        debug_hip_exercise()
    except KeyboardInterrupt:
        print("\n\nDebug session cancelled")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
