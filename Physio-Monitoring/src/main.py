import os, sys, cv2, mediapipe as mp

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.smoothing import MovingAverage
from src.repetition.rep_counter import RepCounter
from src.repetition.shoulder_rep_counter import create_shoulder_counter
from src.feedback.visual_feedback import draw_hud
from src.utils.quality_score import QualityScore
from src.analysis.posture_analysis import *
from src.analysis.angle_calculation import *
from src.ml_predictor import MLExercisePredictor

cap = cv2.VideoCapture(0)

pose = mp.solutions.pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

draw = mp.solutions.drawing_utils

# Initialize ML predictor for exercise classification
ml_predictor = MLExercisePredictor()

# Prediction validation: track consistency across frames
prediction_buffer = []  # Track last 5 predictions for consistency
PREDICTION_BUFFER_SIZE = 5
CONFIDENCE_THRESHOLD = 0.85  # Increased from 0.65 for stricter detection

smooth = {
    "elbow": MovingAverage(3),
    "elbow_extension": MovingAverage(3),
    "shoulder_abduction": MovingAverage(3),
    "shoulder_flexion": MovingAverage(3),
    "shoulder_extension": MovingAverage(3),
    "shoulder_adduction": MovingAverage(3),
    "shoulder_internal_rotation": MovingAverage(3),
    "shoulder_external_rotation": MovingAverage(3),
    "shoulder_horizontal_abduction": MovingAverage(3),
    "shoulder_horizontal_adduction": MovingAverage(3),
    "shoulder_circumduction": MovingAverage(3),
    "knee": MovingAverage(3),
    "hip": MovingAverage(3)
}

# All shoulder exercises
SHOULDER_EXERCISES = [
    "Shoulder Flexion",
    "Shoulder Extension",
    "Shoulder Abduction",
    "Shoulder Adduction",
    "Shoulder Internal Rotation",
    "Shoulder External Rotation",
    "Shoulder Horizontal Abduction",
    "Shoulder Horizontal Adduction",
    "Shoulder Circumduction",
]

ALL_EXERCISES = SHOULDER_EXERCISES + [
    "Elbow Flexion",
    "Elbow Extension",
    "Knee Flexion",
    "Hip Abduction"
]

# Initialize rep counters for all exercises
rep = {}
quality = {}

# Shoulder exercises
for exercise in SHOULDER_EXERCISES:
    rep[exercise] = create_shoulder_counter(exercise)
    quality[exercise] = QualityScore(0, 180)

# Other exercises
rep["Elbow Flexion"] = RepCounter(100, 140)  # 100°=extended, 140°=fully flexed
rep["Elbow Extension"] = RepCounter(140, 100)  # 140°=fully extended, 100°=at rest
rep["Knee Flexion"] = RepCounter(140, 80)  # 140°=extended, 80°=fully flexed
rep["Hip Abduction"] = RepCounter(45, 90)  # 45°=at side, 90°=fully abducted

quality["Elbow Flexion"] = QualityScore(70, 140)
quality["Elbow Extension"] = QualityScore(100, 150)
quality["Knee Flexion"] = QualityScore(90, 165)
quality["Hip Abduction"] = QualityScore(30, 110)

prev = {
    "elbow": None,
    "elbow_extension": None,
    "shoulder_abduction": None,
    "shoulder_flexion": None,
    "shoulder_extension": None,
    "shoulder_adduction": None,
    "shoulder_internal_rotation": None,
    "shoulder_external_rotation": None,
    "shoulder_horizontal_abduction": None,
    "shoulder_horizontal_adduction": None,
    "shoulder_circumduction": None,
    "knee": None,
    "hip": None
}

# store last-seen coordinates per landmark (fallback when visibility low)
coords_prev = {"shoulder": None, "elbow": None, "wrist": None, "hip": None, "knee": None, "ankle": None}
active = None
rest = 0
frame_count = 0

# Initialize display variables
ex = "Detecting"
reps = 0
ang = 0
posture_msg = "Correct"
q = 0

# TUNED PARAMETERS FOR BETTER DETECTION
VISIBLE = 0.5  # ⬆️ Increased to ignore noisy/low-confidence landmarks
ACT = 8        # ⬆️ Increased to require significant motion
NOISE = 0      # ⬇️ Removed noise filter to detect all motion

print("=== Physiotherapy Monitoring System Running ===")
print(f"   Visibility threshold: {VISIBLE}")
print(f"   Motion threshold (ACT): {ACT}")
print(f"   Noise threshold: {NOISE}")


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = pose.process(rgb)

    ex, reps, ang, q = "Detecting", 0, 0, 0
    posture_msg = "Correct"

    if res.pose_landmarks:
        lm = res.pose_landmarks.landmark
        draw.draw_landmarks(frame, res.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)

        # per-landmark coords with fallback to last-seen when visibility is low
        idx_map = {
            "shoulder": 12, "elbow": 14, "wrist": 16,
            "hip": 24, "knee": 26, "ankle": 28
        }

        coords = {}
        # Always read landmark coordinates; use visibility for fallback only
        landmark_vis = {}
        for name, idx in idx_map.items():
            landmark_vis[name] = lm[idx].visibility
            coords[name] = (lm[idx].x, lm[idx].y)
            coords_prev[name] = coords[name]

        # compute angles using available landmarks (use fallback if not all landmarks available)
        angles = {}
        
        # Elbow flexion: shoulder-elbow-wrist
        if coords.get("shoulder") and coords.get("elbow"):
            if coords.get("wrist"):
                raw_angle = elbow_angle(coords["shoulder"], coords["elbow"], coords["wrist"])
            else:
                raw_angle = elbow_angle(coords["shoulder"], coords["elbow"], coords["elbow"])
            angles["elbow"] = smooth["elbow"].update(raw_angle) if raw_angle > 0 else (prev["elbow"] or 0)
            angles["elbow_extension"] = angles["elbow"]  # Same angle, different exercise name
        else:
            angles["elbow"] = prev["elbow"] if prev["elbow"] is not None else 0
            angles["elbow_extension"] = prev.get("elbow_extension", 0) if prev.get("elbow_extension") is not None else 0

        # ========== SHOULDER ANGLES ==========
        
        # Shoulder flexion: hip-shoulder-elbow (sagittal plane)
        if coords.get("hip") and coords.get("shoulder") and coords.get("elbow"):
            raw_angle = shoulder_flexion_angle(coords["shoulder"], coords["elbow"], coords["hip"])
            angles["shoulder_flexion"] = smooth["shoulder_flexion"].update(raw_angle) if raw_angle > 0 else (prev["shoulder_flexion"] or 0)
        else:
            angles["shoulder_flexion"] = prev["shoulder_flexion"] if prev["shoulder_flexion"] is not None else 0

        # Shoulder extension: hip-shoulder-elbow (backward movement)
        if coords.get("hip") and coords.get("shoulder") and coords.get("elbow"):
            raw_angle = shoulder_extension_angle(coords["shoulder"], coords["elbow"], coords["hip"])
            angles["shoulder_extension"] = smooth["shoulder_extension"].update(raw_angle) if raw_angle > 0 else (prev["shoulder_extension"] or 0)
        else:
            angles["shoulder_extension"] = prev["shoulder_extension"] if prev["shoulder_extension"] is not None else 0

        # Shoulder abduction: elbow-shoulder-hip (frontal plane)
        if coords.get("elbow") and coords.get("shoulder") and coords.get("hip"):
            raw_angle = shoulder_abduction_angle(coords["shoulder"], coords["elbow"], coords["hip"])
            angles["shoulder_abduction"] = smooth["shoulder_abduction"].update(raw_angle) if raw_angle > 0 else (prev["shoulder_abduction"] or 0)
        else:
            angles["shoulder_abduction"] = prev["shoulder_abduction"] if prev["shoulder_abduction"] is not None else 0

        # Shoulder adduction: elbow-shoulder-hip (bringing arm down)
        if coords.get("elbow") and coords.get("shoulder") and coords.get("hip"):
            raw_angle = shoulder_abduction_angle(coords["shoulder"], coords["elbow"], coords["hip"])
            angles["shoulder_adduction"] = smooth["shoulder_adduction"].update(raw_angle) if raw_angle > 0 else (prev["shoulder_adduction"] or 0)
        else:
            angles["shoulder_adduction"] = prev["shoulder_adduction"] if prev["shoulder_adduction"] is not None else 0

        # Shoulder internal rotation: shoulder-elbow-wrist
        if coords.get("shoulder") and coords.get("elbow") and coords.get("wrist"):
            raw_angle = shoulder_internal_rotation_angle(coords["shoulder"], coords["elbow"], coords["wrist"])
            angles["shoulder_internal_rotation"] = smooth["shoulder_internal_rotation"].update(raw_angle) if raw_angle > 0 else (prev["shoulder_internal_rotation"] or 0)
        else:
            angles["shoulder_internal_rotation"] = prev["shoulder_internal_rotation"] if prev["shoulder_internal_rotation"] is not None else 0

        # Shoulder external rotation: shoulder-elbow-wrist (opposite rotation)
        if coords.get("shoulder") and coords.get("elbow") and coords.get("wrist"):
            raw_angle = shoulder_external_rotation_angle(coords["shoulder"], coords["elbow"], coords["wrist"])
            angles["shoulder_external_rotation"] = smooth["shoulder_external_rotation"].update(raw_angle) if raw_angle > 0 else (prev["shoulder_external_rotation"] or 0)
        else:
            angles["shoulder_external_rotation"] = prev["shoulder_external_rotation"] if prev["shoulder_external_rotation"] is not None else 0

        # Shoulder horizontal abduction: elbow-shoulder-spine (arm moving back)
        if coords.get("elbow") and coords.get("shoulder") and coords.get("hip"):
            raw_angle = shoulder_horizontal_abduction_angle(coords["shoulder"], coords["elbow"], coords["hip"])
            angles["shoulder_horizontal_abduction"] = smooth["shoulder_horizontal_abduction"].update(raw_angle) if raw_angle > 0 else (prev["shoulder_horizontal_abduction"] or 0)
        else:
            angles["shoulder_horizontal_abduction"] = prev["shoulder_horizontal_abduction"] if prev["shoulder_horizontal_abduction"] is not None else 0

        # Shoulder horizontal adduction: elbow-shoulder-spine (arm moving forward)
        if coords.get("elbow") and coords.get("shoulder") and coords.get("hip"):
            raw_angle = shoulder_horizontal_adduction_angle(coords["shoulder"], coords["elbow"], coords["hip"])
            angles["shoulder_horizontal_adduction"] = smooth["shoulder_horizontal_adduction"].update(raw_angle) if raw_angle > 0 else (prev["shoulder_horizontal_adduction"] or 0)
        else:
            angles["shoulder_horizontal_adduction"] = prev["shoulder_horizontal_adduction"] if prev["shoulder_horizontal_adduction"] is not None else 0

        # Shoulder circumduction: circular motion
        if coords.get("elbow") and coords.get("shoulder") and coords.get("hip"):
            raw_angle = shoulder_circumduction_angle(coords["shoulder"], coords["elbow"], coords["hip"])
            angles["shoulder_circumduction"] = smooth["shoulder_circumduction"].update(raw_angle) if raw_angle > 0 else (prev["shoulder_circumduction"] or 0)
        else:
            angles["shoulder_circumduction"] = prev["shoulder_circumduction"] if prev["shoulder_circumduction"] is not None else 0

        # Knee flexion: hip-knee-ankle
        if coords.get("hip") and coords.get("knee"):
            if coords.get("ankle"):
                raw_angle = knee_angle(coords["hip"], coords["knee"], coords["ankle"])
            else:
                raw_angle = knee_angle(coords["hip"], coords["knee"], coords["knee"])
            angles["knee"] = smooth["knee"].update(raw_angle) if raw_angle > 0 else (prev["knee"] or 0)
        else:
            angles["knee"] = prev["knee"] if prev["knee"] is not None else 0

        # Hip abduction: shoulder-hip-knee
        if coords.get("shoulder") and coords.get("hip") and coords.get("knee"):
            raw_angle = hip_angle(coords["shoulder"], coords["hip"], coords["knee"])
            angles["hip"] = smooth["hip"].update(raw_angle) if raw_angle > 0 else (prev["hip"] or 0)
        else:
            angles["hip"] = prev["hip"] if prev["hip"] is not None else 0

        motion = {}
        for j in angles:
            motion[j] = 0 if prev[j] is None else abs(angles[j] - prev[j])
            prev[j] = angles[j]

        # Debug: Print angles and motion every 30 frames with landmark visibility info
        if frame_count % 30 == 0:
            landmarks_detected = {
                "shoulder": lm[12].visibility, "elbow": lm[14].visibility,
                "wrist": lm[16].visibility, "hip": lm[24].visibility,
                "knee": lm[26].visibility, "ankle": lm[28].visibility
            }
            print(f"Frame {frame_count}: Active={active}, Motion: elbow={motion.get('elbow', 0):.1f}, "
                  f"sh_flex={motion.get('shoulder_flexion', 0):.1f}, sh_abd={motion.get('shoulder_abduction', 0):.1f}")

        # Exercise detection logic - detect motion in all joint categories
        if active is None:
                # Use ML model to predict exercise from current pose
                if ml_predictor.is_ready() and motion:
                    # Only predict if there's significant motion
                    max_motion_val = max(motion.values()) if motion else 0
                    max_motion_joint = max(motion, key=motion.get) if motion else None
                    
                    if max_motion_val > 8:  # Minimal motion threshold to trigger prediction
                        predicted_exercise, confidence = ml_predictor.predict(lm, confidence_threshold=0.0)
                        
                        # Add prediction to buffer for consistency checking
                        if predicted_exercise:
                            prediction_buffer.append((predicted_exercise, confidence, max_motion_joint, max_motion_val))
                            if len(prediction_buffer) > PREDICTION_BUFFER_SIZE:
                                prediction_buffer.pop(0)
                            
                            # Only activate if: high confidence AND motion in relevant area AND consistency
                            is_confident = confidence >= CONFIDENCE_THRESHOLD
                            is_consistent = (len(prediction_buffer) >= 3 and 
                                            all(p[0] == predicted_exercise for p in prediction_buffer[-3:]))
                            
                            # STRICT validation: predicted exercise MUST match actual joint motion
                            motion_valid = False  # Default to INVALID
                            
                            # For Knee Flexion: MUST have knee as PRIMARY and ONLY mover
                            if predicted_exercise == "Knee Flexion":
                                knee_motion = motion.get('knee', 0)
                                shoulder_motion = max(motion.get(key, 0) for key in motion if 'shoulder' in key)
                                elbow_motion = motion.get('elbow', 0)
                                
                                # STRICT: knee must be primary (>10°), shoulders minimal (<2°), elbow minimal (<2°)
                                if knee_motion >= 10 and shoulder_motion < 2 and elbow_motion < 2:
                                    motion_valid = True
                                else:
                                    # Reject if primary motion is NOT in knee
                                    motion_valid = False
                            
                            # For Elbow Flexion: elbow MUST be primary mover (>8°), not shoulders
                            elif predicted_exercise == "Elbow Flexion":
                                elbow_motion = motion.get('elbow', 0)
                                shoulder_motion = max(motion.get(key, 0) for key in motion if 'shoulder' in key)
                                knee_motion = motion.get('knee', 0)
                                
                                # STRICT: elbow must be primary (>8°), shoulders/knee minimal
                                if elbow_motion >= 8 and elbow_motion > shoulder_motion and knee_motion < 3:
                                    motion_valid = True
                            
                            # For Shoulder exercises: shoulders MUST be primary (>8°), not knee/elbow
                            elif predicted_exercise in SHOULDER_EXERCISES:
                                shoulder_motion = max(motion.get(key, 0) for key in motion if 'shoulder' in key)
                                elbow_motion = motion.get('elbow', 0)
                                knee_motion = motion.get('knee', 0)
                                
                                # STRICT: shoulder must be primary (>8°) and clearly dominant
                                if shoulder_motion >= 8 and shoulder_motion > elbow_motion and knee_motion < 3:
                                    motion_valid = True
                            
                            if is_confident and motion_valid and is_consistent:
                                active = predicted_exercise
                                print(f"[DETECTED] Exercise: {active} (confidence: {confidence:.2%}, motion_joint: {max_motion_joint}, motion_valid: {motion_valid})")
                                prediction_buffer = []  # Clear buffer after activation
                            elif predicted_exercise and frame_count % 60 == 0:
                                # Debug: show why prediction was rejected
                                print(f"[REJECTED] {predicted_exercise} - conf:{is_confident}, valid:{motion_valid}, consist:{is_consistent}")
                        else:
                            prediction_buffer = []

        # Exercise-specific posture validation and get correct angle
        if active:
            # Map exercise name to angle key
            angle_map = {
                "Elbow Flexion": "elbow",
                "Elbow Extension": "elbow_extension",
                "Shoulder Flexion": "shoulder_flexion",
                "Shoulder Extension": "shoulder_extension",
                "Shoulder Abduction": "shoulder_abduction",
                "Shoulder Adduction": "shoulder_adduction",
                "Shoulder Internal Rotation": "shoulder_internal_rotation",
                "Shoulder External Rotation": "shoulder_external_rotation",
                "Shoulder Horizontal Abduction": "shoulder_horizontal_abduction",
                "Shoulder Horizontal Adduction": "shoulder_horizontal_adduction",
                "Shoulder Circumduction": "shoulder_circumduction",
                "Knee Flexion": "knee",
                "Hip Abduction": "hip"
            }
            
            joint = angle_map.get(active)
            if joint and joint in angles:
                ang = angles[joint]
                
                # Validate posture based on exercise
                if active == "Elbow Flexion":
                    posture_msg = "Correct" if 100 < ang < 150 else "Wrong: Bend elbow to 90°"
                
                elif active == "Elbow Extension":
                    posture_msg = "Correct" if 100 < ang < 160 else "Wrong: Straighten arm"
                
                # ========== SHOULDER EXERCISES ==========
                elif active == "Shoulder Flexion":
                    posture_msg = "Correct" if 20 < ang < 170 else "Wrong: Raise arm forward"
                
                elif active == "Shoulder Extension":
                    posture_msg = "Correct" if 0 < ang < 100 else "Wrong: Extend arm backward"
                
                elif active == "Shoulder Abduction":
                    posture_msg = "Correct" if 20 < ang < 170 else "Wrong: Raise arm sideways"
                
                elif active == "Shoulder Adduction":
                    posture_msg = "Correct" if 20 < ang < 170 else "Wrong: Lower arm to body"
                
                elif active == "Shoulder Internal Rotation":
                    posture_msg = "Correct" if 30 < ang < 170 else "Wrong: Rotate arm inward"
                
                elif active == "Shoulder External Rotation":
                    posture_msg = "Correct" if 30 < ang < 170 else "Wrong: Rotate arm outward"
                
                elif active == "Shoulder Horizontal Abduction":
                    posture_msg = "Correct" if 40 < ang < 170 else "Wrong: Move arm backward"
                
                elif active == "Shoulder Horizontal Adduction":
                    posture_msg = "Correct" if 40 < ang < 170 else "Wrong: Move arm across body"
                
                elif active == "Shoulder Circumduction":
                    posture_msg = "Correct" if 0 < ang < 360 else "Wrong: Move arm in circle"
                
                else:
                    posture_msg = "Correct"
                
                # Update rep counter
                reps = rep[active].update(ang, posture_ok=(posture_msg == "Correct"))
                quality[active].update(ang)
                q = quality[active].compute()
                ex = active
                
                # Debug: print reps when they increase
                if frame_count % 30 == 0:  # Print every 30 frames (1 second)
                        confidence = "N/A"
                        if ml_predictor.is_ready():
                            _, confidence = ml_predictor.predict(lm, confidence_threshold=0.0)
                            confidence = f"{confidence:.2%}"
                        print(f"Frame {frame_count}: {active} - Angle: {ang:.1f}° - Reps: {reps} - Posture: {posture_msg} - ML Conf: {confidence}")

                if motion[joint] < 2:
                    rest += 1
                else:
                    rest = 0

                if rest > 90:  # Increased from 30 frames (1 sec) to 90 frames (3 sec)
                    print(f"[ENDED] Exercise: {active} (reps: {reps})")
                    # Keep displaying the final reps for 60 more frames before clearing
                    active = None
                    rest = 0
                    # DON'T reset reps here - let them display
                    # ex, reps will be shown for another 2 seconds
            else:
                active = None
                reps = 0
                ex = "Detecting"
        else:
            # Reset display when not active ONLY after 60 frames (2 seconds)
            # This allows reps to be displayed for a short time after exercise ends
            if rest > 60:
                ex = "Detecting"
                reps = 0
                ang = 0
                posture_msg = "Correct"
                q = 0
            rest += 1

        draw_hud(frame, ex, reps, ang, posture_msg, q)

    # Display the frame with all overlays
    cv2.imshow("Physio Monitoring", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
