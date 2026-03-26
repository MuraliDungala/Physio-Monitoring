import sys
import os
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
import base64
import warnings

# Initialize logger
logger = logging.getLogger(__name__)

# Try to import MediaPipe with comprehensive error handling
MEDIAPIPE_AVAILABLE = False
mp_pose = None
mp_drawing = None

try:
    import mediapipe as mp
    if hasattr(mp, 'solutions'):
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        MEDIAPIPE_AVAILABLE = True
    else:
        # Try alternate import path for newer versions
        from mediapipe.python.solutions import pose as mp_pose_module
        from mediapipe.python.solutions import drawing_utils as mp_drawing_module
        mp_pose = mp_pose_module
        mp_drawing = mp_drawing_module
        MEDIAPIPE_AVAILABLE = True
except Exception as e:
    logger.warning(f"MediaPipe not available: {e}. Using stub implementation for testing.")
    warnings.warn(f"MediaPipe loading failed: {e}. Pose detection will use stub data.")
    MEDIAPIPE_AVAILABLE = False

# If MediaPipe is not available, create a stub class
if not MEDIAPIPE_AVAILABLE:
    class PoseStub:
        """Stub Pose class for when MediaPipe fails to load"""
        def __init__(self, *args, **kwargs):
            self.POSE_CONNECTIONS = []
        
        def process(self, image):
            # Return a stub landmarksresult with no landmarks (no pose detected)
            class StubLandmarks:
                def __init__(self):
                    self.pose_landmarks = None
                    self.pose_world_landmarks = None
                    self.segmentation_mask = None
            return StubLandmarks()
    
    class DrawingUtilsStub:
        """Stub drawing_utils when MediaPipe is unavailable"""
        class DrawingSpec:
            def __init__(self, color=(0,255,0), thickness=2, circle_radius=3):
                self.color = color
                self.thickness = thickness
                self.circle_radius = circle_radius
        
        @staticmethod
        def draw_landmarks(*args, **kwargs):
            pass
    
    class MPPoseStub:
        """Stub mp.solutions.pose"""
        Pose = PoseStub
        POSE_CONNECTIONS = []
    
    mp_pose = MPPoseStub()
    mp_drawing = DrawingUtilsStub()

# Initialize logger
logger = logging.getLogger(__name__)

# Add the original Physio-Monitoring path to import existing modules
ORIGINAL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Physio-Monitoring'))
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ORIGINAL_PATH)
sys.path.insert(0, BACKEND_PATH)

# Import state manager
from exercise_state_manager import ExerciseStateManager

# Import existing modules
try:
    from src.utils.smoothing import MovingAverage
    from src.repetition.rep_counter import RepCounter
    from src.repetition.shoulder_rep_counter import create_shoulder_counter
    from src.utils.quality_score import QualityScore
    from src.analysis.posture_analysis import *
    from src.analysis.angle_calculation import *
    from src.ml_predictor import MLExercisePredictor
    ORIGINAL_MODULES_AVAILABLE = True
except ImportError:
    print("Warning: Could not import original Physio-Monitoring modules")
    ORIGINAL_MODULES_AVAILABLE = False

class ExerciseEngine:
    def __init__(self):
        self.mp_pose = mp_pose
        self.mp_drawing = mp_drawing
        self.pose = None
        self.current_landmarks = None
        self.rep_count = 0
        self.last_rep_state = False
        
        # Initialize state manager for proper multi-exercise support
        self.state_manager = ExerciseStateManager()
        
        try:
            self.pose = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except Exception as e:
            logger.warning(f"Failed to initialize MediaPipe Pose: {e}")
            self.pose = None
        
        # Initialize ML predictor if available
        self.ml_predictor = MLExercisePredictor() if ORIGINAL_MODULES_AVAILABLE else None
        
        # Exercise definitions
        self.SHOULDER_EXERCISES = [
            "Shoulder Flexion", "Shoulder Extension", "Shoulder Abduction", "Shoulder Adduction",
            "Shoulder Internal Rotation", "Shoulder External Rotation",
            "Shoulder Horizontal Abduction", "Shoulder Horizontal Adduction", "Shoulder Circumduction"
        ]
        
        self.ALL_EXERCISES = self.SHOULDER_EXERCISES + [
            "Elbow Flexion", "Elbow Extension", "Knee Flexion", "Hip Abduction"
        ]
        
        # Initialize exercise-specific components
        self.rep_counters = {}
        self.quality_scorers = {}
        self.smoothers = {}
        self.previous_angles = {}
        
        self._initialize_exercise_components()
        
        # State tracking
        self.active_exercise = None
        self.prediction_buffer = []
        self.PREDICTION_BUFFER_SIZE = 5
        self.CONFIDENCE_THRESHOLD = 0.85
        
        # Parameters
        self.VISIBLE_THRESHOLD = 0.5
        self.MOTION_THRESHOLD = 8
        self.REST_FRAMES_THRESHOLD = 90
        
        # Frame counter
        self.frame_count = 0
        
    def _initialize_exercise_components(self):
        """Initialize rep counters, quality scorers, and smoothers for all exercises"""
        if not ORIGINAL_MODULES_AVAILABLE:
            return
            
        # Initialize smoothers
        angle_keys = [
            "elbow", "elbow_extension", "shoulder_abduction", "shoulder_flexion", "shoulder_extension",
            "shoulder_adduction", "shoulder_internal_rotation", "shoulder_external_rotation",
            "shoulder_horizontal_abduction", "shoulder_horizontal_adduction", "shoulder_circumduction",
            "knee", "hip"
        ]
        
        for key in angle_keys:
            self.smoothers[key] = MovingAverage(5)
            self.previous_angles[key] = None
        
        # Initialize rep counters and quality scorers
        for exercise in self.SHOULDER_EXERCISES:
            self.rep_counters[exercise] = create_shoulder_counter(exercise)
            self.quality_scorers[exercise] = QualityScore(0, 180)
        
        # Other exercises
        self.rep_counters["Elbow Flexion"] = RepCounter(100, 140)
        self.rep_counters["Elbow Extension"] = RepCounter(140, 100)
        self.rep_counters["Knee Flexion"] = RepCounter(140, 80)
        self.rep_counters["Hip Abduction"] = RepCounter(45, 90)
        
        self.quality_scorers["Elbow Flexion"] = QualityScore(70, 140)
        self.quality_scorers["Elbow Extension"] = QualityScore(100, 150)
        self.quality_scorers["Knee Flexion"] = QualityScore(90, 165)
        self.quality_scorers["Hip Abduction"] = QualityScore(30, 110)
    
    def process_frame(self, frame: np.ndarray, selected_exercise: Optional[str] = None) -> Dict[str, Any]:
        """Process a single frame and return exercise analysis"""
        self.frame_count += 1
        
        # Initialize result
        result = {
            "exercise": "Detecting",
            "reps": 0,
            "angle": 0,
            "posture_message": "Correct",
            "quality_score": 0,
            "confidence": None,
            "landmarks_detected": False,
            "skeleton_data": None,
            "skeleton_image": None
        }
        
        if not self.pose:
            # Fallback when MediaPipe is not available
            result["posture_message"] = "MediaPipe not available - using fallback mode"
            return result
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            result["landmarks_detected"] = True
            result["skeleton_data"] = results.pose_landmarks.landmark
            self.current_landmarks = results.pose_landmarks.landmark
            
            # Draw skeleton on frame
            skeleton_frame = self.draw_skeleton(frame, results.pose_landmarks.landmark)
            
            # Convert skeleton frame to base64 for transmission
            _, buffer = cv2.imencode('.jpg', skeleton_frame)
            result["skeleton_image"] = base64.b64encode(buffer).decode('utf-8')
            
            # Extract coordinates and compute angles
            coords, angles, motion = self._extract_pose_data(results.pose_landmarks.landmark)
            
            # Log extraction results
            num_landmarks = len([l for l in results.pose_landmarks.landmark if l.visibility > 0.3])
            logger.info(f"Frame {self.frame_count}: Detected {num_landmarks} visible landmarks, extracted {len(coords)} coords, computed {len(angles)} angles")
            
            # Exercise detection or tracking
            if selected_exercise:
                # Exercise-specific mode: only track selected exercise
                result = self._track_selected_exercise(selected_exercise, angles, motion, result)
            else:
                # Auto-detection mode
                result = self._auto_detect_exercise(angles, motion, results.pose_landmarks.landmark, result)
        
        return result
    
    def draw_skeleton(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """Draw skeleton on frame using MediaPipe landmarks"""
        # Create a copy of the frame
        skeleton_frame = frame.copy()
        
        # MediaPipe pose connections
        POSE_CONNECTIONS = [
            (11, 12),  # shoulders
            (11, 13),  # left shoulder to elbow
            (13, 15),  # left elbow to wrist
            (12, 14),  # right shoulder to elbow
            (14, 16),  # right elbow to wrist
            (11, 23),  # left shoulder to hip
            (12, 24),  # right shoulder to hip
            (23, 24),  # hips
            (23, 25),  # left hip to knee
            (25, 27),  # left knee to ankle
            (24, 26),  # right hip to knee
            (26, 28),  # right knee to ankle
            (0, 1), (1, 2), (2, 3), (3, 7),  # face
            (0, 4), (4, 5), (5, 6), (6, 8),  # face
            (9, 10),  # face
            (14, 16),  # right arm
            (11, 13),  # left arm
        ]
        
        # Convert landmarks to pixel coordinates
        h, w = frame.shape[:2]
        points = []
        for landmark in landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            points.append((x, y))
        
        # Draw connections
        for connection in POSE_CONNECTIONS:
            start_idx, end_idx = connection
            if start_idx < len(points) and end_idx < len(points):
                start_point = points[start_idx]
                end_point = points[end_idx]
                
                # Draw line with thickness and color
                cv2.line(skeleton_frame, start_point, end_point, (0, 255, 0), 3)
        
        # Draw landmarks
        for i, point in enumerate(points):
            if i < len(landmarks):
                confidence = landmarks[i].visibility
                if confidence > 0.5:  # Only draw visible landmarks
                    # Color based on body part
                    if i in [11, 12]:  # shoulders - blue
                        color = (255, 0, 0)
                    elif i in [13, 14]:  # elbows - yellow
                        color = (0, 255, 255)
                    elif i in [15, 16]:  # wrists - cyan
                        color = (255, 255, 0)
                    elif i in [23, 24]:  # hips - magenta
                        color = (255, 0, 255)
                    elif i in [25, 26]:  # knees - orange
                        color = (0, 165, 255)
                    elif i in [27, 28]:  # ankles - purple
                        color = (128, 0, 128)
                    else:  # other joints - green
                        color = (0, 255, 0)
                    
                    cv2.circle(skeleton_frame, point, 5, color, -1)
                    cv2.circle(skeleton_frame, point, 7, (255, 255, 255), 2)
        
        # Add frame info
        cv2.putText(skeleton_frame, f"Frame: {self.frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(skeleton_frame, "Skeleton Tracking Active", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return skeleton_frame
    
    def _extract_pose_data(self, landmarks) -> Tuple[Dict, Dict, Dict]:
        """Extract coordinates and compute angles from landmarks"""
        # MediaPipe landmark mapping - includes head landmarks for neck detection
        idx_map = {
            # Head landmarks (for neck angle calculation)
            "nose": 0,
            "left_ear": 7, "right_ear": 8,
            
            # Body joints
            "left_shoulder": 11, "right_shoulder": 12,
            "left_elbow": 13, "right_elbow": 14, 
            "left_wrist": 15, "right_wrist": 16,
            "left_hip": 23, "right_hip": 24,
            "left_knee": 25, "right_knee": 26,
            "left_ankle": 27, "right_ankle": 28,
            
            # Hand landmarks (for wrist angle refinement)
            "left_pinky": 21, "right_pinky": 22,
            "left_index": 19, "right_index": 20,
        }
        
        # Extract coordinates with visibility threshold
        coords = {}
        for name, idx in idx_map.items():
            if idx < len(landmarks):
                lm = landmarks[idx]
                # Lowered visibility threshold to 0.1 for better landmark detection
                # Especially important for neck exercises (nose and ears often weakly detected)
                # Previous was 0.2, which filtered out too many landmarks
                if lm.visibility > 0.1:
                    coords[name] = (lm.x, lm.y, lm.z)
        
        # Debug: Log coordinate extraction
        if len(coords) < 5:
            logger.debug(f"Warning: Only {len(coords)} landmarks extracted (need at least 5)")
        
        # Compute angles using basic geometry
        angles = self._compute_angles_basic(coords)
        
        # Debug: Log angle computation
        if len(angles) == 0:
            logger.debug(f"Warning: No angles computed from {len(coords)} landmarks")
        
        # Compute motion
        motion = {}
        for joint in angles:
            if self.previous_angles.get(joint) is not None:
                motion[joint] = abs(angles[joint] - self.previous_angles[joint])
            else:
                motion[joint] = 0
            self.previous_angles[joint] = angles[joint]
        
        return coords, angles, motion
    
    def _compute_angles_basic(self, coords: Dict) -> Dict:
        """Compute joint angles using basic geometry"""
        angles = {}
        
        try:
            # Right elbow angle (shoulder-elbow-wrist)
            try:
                if "right_shoulder" in coords and "right_elbow" in coords and "right_wrist" in coords:
                    angle = self._calculate_angle_3d(
                        coords["right_shoulder"], 
                        coords["right_elbow"], 
                        coords["right_wrist"]
                    )
                    angles["right_elbow"] = angle
            except Exception as e:
                logger.debug(f"Right elbow angle error: {e}")
            
            # Left elbow angle (shoulder-elbow-wrist)
            try:
                if "left_shoulder" in coords and "left_elbow" in coords and "left_wrist" in coords:
                    angle = self._calculate_angle_3d(
                        coords["left_shoulder"], 
                        coords["left_elbow"], 
                        coords["left_wrist"]
                    )
                    angles["left_elbow"] = angle
            except Exception as e:
                logger.debug(f"Left elbow angle error: {e}")
            
            # Shoulder angles - compute from BOTH sides and average for bilateral movements
            # This prevents double-counting when performing with both arms simultaneously
            
            # Raw angles for flexion and extension
            right_flex_raw = 0
            left_flex_raw = 0
            right_ext_raw = 0
            left_ext_raw = 0
            
            if coords.get("right_shoulder") and coords.get("right_elbow") and coords.get("right_hip"):
                # Compute right side raw angles (no smoothing yet)
                right_flex_raw = shoulder_flexion_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_hip"])
                right_ext_raw = shoulder_extension_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_hip"])
            
            if coords.get("left_shoulder") and coords.get("left_elbow") and coords.get("left_hip"):
                # Compute left side raw angles (no smoothing yet)
                left_flex_raw = shoulder_flexion_angle(coords["left_shoulder"], coords["left_elbow"], coords["left_hip"])
                left_ext_raw = shoulder_extension_angle(coords["left_shoulder"], coords["left_elbow"], coords["left_hip"])
            
            # Average raw flexion angles, then smooth ONCE
            if left_flex_raw > 0 and right_flex_raw > 0:
                avg_flex = (left_flex_raw + right_flex_raw) / 2
                angles["shoulder_flexion"] = self.smoothers["shoulder_flexion"].update(avg_flex)
                logger.info(f"Shoulder flexion (bilateral avg): {angles['shoulder_flexion']:.1f}° (left={left_flex_raw:.1f}°, right={right_flex_raw:.1f}°)")
            elif right_flex_raw > 0:
                angles["shoulder_flexion"] = self.smoothers["shoulder_flexion"].update(right_flex_raw)
                logger.info(f"Shoulder flexion (right): {angles['shoulder_flexion']:.1f}°")
            elif left_flex_raw > 0:
                angles["shoulder_flexion"] = self.smoothers["shoulder_flexion"].update(left_flex_raw)
                logger.info(f"Shoulder flexion (left): {angles['shoulder_flexion']:.1f}°")
            
            # Average raw extension angles, then smooth ONCE
            if left_ext_raw > 0 and right_ext_raw > 0:
                avg_ext = (left_ext_raw + right_ext_raw) / 2
                angles["shoulder_extension"] = self.smoothers["shoulder_extension"].update(avg_ext)
                logger.info(f"Shoulder extension (bilateral avg): {angles['shoulder_extension']:.1f}°")
            elif right_ext_raw > 0:
                angles["shoulder_extension"] = self.smoothers["shoulder_extension"].update(right_ext_raw)
                logger.info(f"Shoulder extension (right): {angles['shoulder_extension']:.1f}°")
            elif left_ext_raw > 0:
                angles["shoulder_extension"] = self.smoothers["shoulder_extension"].update(left_ext_raw)
                logger.info(f"Shoulder extension (left): {angles['shoulder_extension']:.1f}°")
            
            # Compute shoulder angles from BOTH sides, then consolidate
            # KEY: Compute raw angles first, average them, then apply smoothing ONCE
            
            # Raw angles for abduction/adduction
            right_abd_raw = 0
            left_abd_raw = 0
            if coords.get("right_elbow") and coords.get("right_shoulder") and coords.get("right_hip"):
                right_abd_raw = shoulder_abduction_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_hip"])
            if coords.get("left_elbow") and coords.get("left_shoulder") and coords.get("left_hip"):
                left_abd_raw = shoulder_abduction_angle(coords["left_shoulder"], coords["left_elbow"], coords["left_hip"])
            
            # Average raw angles, then smooth once
            if left_abd_raw > 0 and right_abd_raw > 0:
                avg_abd = (left_abd_raw + right_abd_raw) / 2
                angles["shoulder_abduction"] = self.smoothers["shoulder_abduction"].update(avg_abd)
                angles["shoulder_adduction"] = self.smoothers["shoulder_adduction"].update(avg_abd)
                logger.info(f"Shoulder abduction (bilateral avg): {angles['shoulder_abduction']:.1f}° (left={left_abd_raw:.1f}°, right={right_abd_raw:.1f}°)")
            elif right_abd_raw > 0:
                angles["shoulder_abduction"] = self.smoothers["shoulder_abduction"].update(right_abd_raw)
                angles["shoulder_adduction"] = self.smoothers["shoulder_adduction"].update(right_abd_raw)
            elif left_abd_raw > 0:
                angles["shoulder_abduction"] = self.smoothers["shoulder_abduction"].update(left_abd_raw)
                angles["shoulder_adduction"] = self.smoothers["shoulder_adduction"].update(left_abd_raw)
            
            # Raw angles for horizontal abduction/adduction
            right_habd_raw = 0
            left_habd_raw = 0
            right_hadd_raw = 0
            left_hadd_raw = 0
            if coords.get("right_elbow") and coords.get("right_shoulder") and coords.get("right_hip"):
                right_habd_raw = shoulder_horizontal_abduction_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_hip"])
                right_hadd_raw = shoulder_horizontal_adduction_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_hip"])
            if coords.get("left_elbow") and coords.get("left_shoulder") and coords.get("left_hip"):
                left_habd_raw = shoulder_horizontal_abduction_angle(coords["left_shoulder"], coords["left_elbow"], coords["left_hip"])
                left_hadd_raw = shoulder_horizontal_adduction_angle(coords["left_shoulder"], coords["left_elbow"], coords["left_hip"])
            
            # Average and smooth horizontal abduction
            if left_habd_raw > 0 and right_habd_raw > 0:
                avg_habd = (left_habd_raw + right_habd_raw) / 2
                angles["shoulder_horizontal_abduction"] = self.smoothers["shoulder_horizontal_abduction"].update(avg_habd)
            elif right_habd_raw > 0:
                angles["shoulder_horizontal_abduction"] = self.smoothers["shoulder_horizontal_abduction"].update(right_habd_raw)
            elif left_habd_raw > 0:
                angles["shoulder_horizontal_abduction"] = self.smoothers["shoulder_horizontal_abduction"].update(left_habd_raw)
            
            # Average and smooth horizontal adduction
            if left_hadd_raw > 0 and right_hadd_raw > 0:
                avg_hadd = (left_hadd_raw + right_hadd_raw) / 2
                angles["shoulder_horizontal_adduction"] = self.smoothers["shoulder_horizontal_adduction"].update(avg_hadd)
            elif right_hadd_raw > 0:
                angles["shoulder_horizontal_adduction"] = self.smoothers["shoulder_horizontal_adduction"].update(right_hadd_raw)
            elif left_hadd_raw > 0:
                angles["shoulder_horizontal_adduction"] = self.smoothers["shoulder_horizontal_adduction"].update(left_hadd_raw)
            
            # Raw angles for circumduction
            right_circ_raw = 0
            left_circ_raw = 0
            if coords.get("right_elbow") and coords.get("right_shoulder") and coords.get("right_hip"):
                right_circ_raw = shoulder_circumduction_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_hip"])
            if coords.get("left_elbow") and coords.get("left_shoulder") and coords.get("left_hip"):
                left_circ_raw = shoulder_circumduction_angle(coords["left_shoulder"], coords["left_elbow"], coords["left_hip"])
            
            # Average and smooth circumduction
            if left_circ_raw > 0 and right_circ_raw > 0:
                avg_circ = (left_circ_raw + right_circ_raw) / 2
                angles["shoulder_circumduction"] = self.smoothers["shoulder_circumduction"].update(avg_circ)
            elif right_circ_raw > 0:
                angles["shoulder_circumduction"] = self.smoothers["shoulder_circumduction"].update(right_circ_raw)
            elif left_circ_raw > 0:
                angles["shoulder_circumduction"] = self.smoothers["shoulder_circumduction"].update(left_circ_raw)
            
            # Internal/External rotation angles - compute RAW for both sides
            right_int_rot_raw = 0
            left_int_rot_raw = 0
            right_ext_rot_raw = 0
            left_ext_rot_raw = 0
            
            if coords.get("right_shoulder") and coords.get("right_elbow") and coords.get("right_wrist"):
                right_int_rot_raw = shoulder_internal_rotation_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_wrist"])
                right_ext_rot_raw = shoulder_external_rotation_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_wrist"])
            
            if coords.get("left_shoulder") and coords.get("left_elbow") and coords.get("left_wrist"):
                left_int_rot_raw = shoulder_internal_rotation_angle(coords["left_shoulder"], coords["left_elbow"], coords["left_wrist"])
                left_ext_rot_raw = shoulder_external_rotation_angle(coords["left_shoulder"], coords["left_elbow"], coords["left_wrist"])
            
            # Average and smooth internal rotation
            if left_int_rot_raw > 0 and right_int_rot_raw > 0:
                avg_int_rot = (left_int_rot_raw + right_int_rot_raw) / 2
                angles["shoulder_internal_rotation"] = self.smoothers["shoulder_internal_rotation"].update(avg_int_rot)
            elif right_int_rot_raw > 0:
                angles["shoulder_internal_rotation"] = self.smoothers["shoulder_internal_rotation"].update(right_int_rot_raw)
            elif left_int_rot_raw > 0:
                angles["shoulder_internal_rotation"] = self.smoothers["shoulder_internal_rotation"].update(left_int_rot_raw)
            
            # Average and smooth external rotation
            if left_ext_rot_raw > 0 and right_ext_rot_raw > 0:
                avg_ext_rot = (left_ext_rot_raw + right_ext_rot_raw) / 2
                angles["shoulder_external_rotation"] = self.smoothers["shoulder_external_rotation"].update(avg_ext_rot)
            elif right_ext_rot_raw > 0:
                angles["shoulder_external_rotation"] = self.smoothers["shoulder_external_rotation"].update(right_ext_rot_raw)
            elif left_ext_rot_raw > 0:
                angles["shoulder_external_rotation"] = self.smoothers["shoulder_external_rotation"].update(left_ext_rot_raw)
            
            # Right knee angle (hip-knee-ankle)
            try:
                if "right_hip" in coords and "right_knee" in coords and "right_ankle" in coords:
                    angle = self._calculate_angle_3d(
                        coords["right_hip"], 
                        coords["right_knee"], 
                        coords["right_ankle"]
                    )
                    angles["right_knee"] = angle
            except Exception as e:
                logger.debug(f"Right knee angle error: {e}")
            
            # Left knee angle (hip-knee-ankle)
            try:
                if "left_hip" in coords and "left_knee" in coords and "left_ankle" in coords:
                    angle = self._calculate_angle_3d(
                        coords["left_hip"], 
                        coords["left_knee"], 
                        coords["left_ankle"]
                    )
                    angles["left_knee"] = angle
            except Exception as e:
                logger.debug(f"Left knee angle error: {e}")
            
            # Right hip angle - Measure BOTH abduction (lateral) and flexion
            try:
                if "right_hip" in coords and "right_knee" in coords:
                    # Always calculate lateral angle for hip abduction
                    lateral_angle = self._calculate_lateral_angle(coords["right_hip"], coords["right_knee"])
                    angles["right_hip_abduction"] = lateral_angle
                    logger.debug(f"Right hip abduction angle (lateral): {lateral_angle:.1f}°")
                    
                    # Also calculate flexion angle if we have the shoulder landmark
                    if "right_shoulder" in coords:
                        flexion_angle = self._calculate_angle_3d(
                            coords["right_shoulder"], 
                            coords["right_hip"], 
                            coords["right_knee"]
                        )
                        angles["right_hip_flexion"] = flexion_angle
                        logger.debug(f"Right hip flexion angle: {flexion_angle:.1f}°")
                    
            except Exception as e:
                logger.debug(f"Right hip angle error: {e}")
            
            # Left hip angle - Measure BOTH abduction (lateral) and flexion
            try:
                if "left_hip" in coords and "left_knee" in coords:
                    # Always calculate lateral angle for hip abduction
                    lateral_angle = self._calculate_lateral_angle(coords["left_hip"], coords["left_knee"])
                    angles["left_hip_abduction"] = lateral_angle
                    logger.debug(f"Left hip abduction angle (lateral): {lateral_angle:.1f}°")
                    
                    # Also calculate flexion angle if we have the shoulder landmark
                    if "left_shoulder" in coords:
                        flexion_angle = self._calculate_angle_3d(
                            coords["left_shoulder"], 
                            coords["left_hip"], 
                            coords["left_knee"]
                        )
                        angles["left_hip_flexion"] = flexion_angle
                        logger.debug(f"Left hip flexion angle: {flexion_angle:.1f}°")
                    
            except Exception as e:
                logger.debug(f"Left hip angle error: {e}")
            
            # Right ankle angle (knee-ankle-hip)
            try:
                if "right_knee" in coords and "right_ankle" in coords and "right_hip" in coords:
                    angle = self._calculate_angle_3d(
                        coords["right_knee"], 
                        coords["right_ankle"], 
                        coords["right_hip"]
                    )
                    angles["right_ankle"] = angle
            except Exception as e:
                logger.debug(f"Right ankle angle error: {e}")
            
            # Left ankle angle (knee-ankle-hip)
            try:
                if "left_knee" in coords and "left_ankle" in coords and "left_hip" in coords:
                    angle = self._calculate_angle_3d(
                        coords["left_knee"], 
                        coords["left_ankle"], 
                        coords["left_hip"]
                    )
                    angles["left_ankle"] = angle
            except Exception as e:
                logger.debug(f"Left ankle angle error: {e}")
            
            # Neck flexion/extension angle - improved calculation using Y displacement
            try:
                if "nose" in coords and "left_shoulder" in coords and "right_shoulder" in coords:
                    # Get shoulder midpoint for reference
                    shoulder_y = (coords["left_shoulder"][1] + coords["right_shoulder"][1]) / 2
                    nose_y = coords["nose"][1]
                    
                    # Vertical offset in image coordinates (0-1 range)
                    # Image Y increases downward, so:
                    # - nose_y < shoulder_y means head is above shoulders (extended) 
                    # - nose_y > shoulder_y means head is below shoulders (flexed)
                    vertical_offset = nose_y - shoulder_y  # Negative = extended, Positive = flexed
                    
                    # Convert vertical offset to angle range
                    # More sensitive scaling: use full range mapping
                    # Clamp offset to reasonable range [-0.2, 0.3] which covers most neck motion
                    vertical_offset = max(-0.2, min(0.3, vertical_offset))
                    
                    if vertical_offset < 0:
                        # Head extension (nose above shoulder): range 20-50° (narrower for extension)
                        # Maps -0.2 to 20°, 0 to 50°
                        neck_angle = 50 + vertical_offset * 150
                    else:
                        # Head flexion (nose below shoulder): range 50-85° (narrower for flexion)
                        # Maps 0 to 50°, +0.3 to 95° (clamped to 85°)
                        neck_angle = 50 + vertical_offset * 117
                    
                    # Clamp angle to reasonable range
                    angles["neck_flexion"] = max(20, min(85, neck_angle))
                    angles["neck_extension"] = max(20, min(85, 105 - neck_angle))  # Complementary angle
                    angles["neck_rotation"] = 45  # Default neutral rotation when not calculating it
                    
                    logger.info(f"Neck flexion angle: {angles['neck_flexion']:.1f}° (offset={vertical_offset:.3f}, raw={neck_angle:.1f}°)")
                    
            except Exception as e:
                logger.debug(f"Neck flexion/extension angle error: {e}")
            
            # Neck rotation angle - improved using ears and nose position
            try:
                if "left_ear" in coords and "right_ear" in coords and "nose" in coords:
                    left_ear = coords["left_ear"]
                    right_ear = coords["right_ear"]
                    nose = coords["nose"]
                    
                    # Calculate rotation based on nose position relative to ears
                    ear_midpoint_x = (left_ear[0] + right_ear[0]) / 2
                    ear_distance = right_ear[0] - left_ear[0]
                    
                    if ear_distance > 0:
                        # Lateral offset as fraction of ear separation
                        # -1 = full left rotation, +1 = full right rotation
                        rotation_ratio = (nose[0] - ear_midpoint_x) / (ear_distance / 2)
                        rotation_ratio = max(-1, min(1, rotation_ratio))  # Clamp to [-1, 1]
                        
                        # Map to angle: -1 = 10°, 0 = 45°, +1 = 80°
                        neck_rotation = 45 + rotation_ratio * 35
                        angles["neck_rotation"] = max(10, min(80, neck_rotation))
                    else:
                        # Fallback if ears too close
                        angles["neck_rotation"] = 45
                    
                    logger.debug(f"Neck rotation angle: {angles['neck_rotation']:.1f}°")
                    
            except Exception as e:
                logger.debug(f"Neck rotation angle error: {e}")
            
            
            
            # Right wrist angle (elbow-wrist-hand_extension)
            try:
                if "right_elbow" in coords and "right_wrist" in coords:
                    if "right_index" in coords:
                        angle = self._calculate_angle_3d(
                            coords["right_elbow"],
                            coords["right_wrist"],
                            coords["right_index"]
                        )
                        angles["right_wrist"] = angle
                    else:
                        # Fallback to shoulder-wrist-elbow
                        if "right_shoulder" in coords:
                            angle = self._calculate_angle_3d(
                                coords["right_shoulder"],
                                coords["right_wrist"],
                                coords["right_elbow"]
                            )
                            angles["right_wrist"] = angle
            except Exception as e:
                logger.debug(f"Right wrist angle error: {e}")
            
            # Left wrist angle (elbow-wrist-hand_extension)
            try:
                if "left_elbow" in coords and "left_wrist" in coords:
                    if "left_index" in coords:
                        angle = self._calculate_angle_3d(
                            coords["left_elbow"],
                            coords["left_wrist"],
                            coords["left_index"]
                        )
                        angles["left_wrist"] = angle
                    else:
                        # Fallback to shoulder-wrist-elbow
                        if "left_shoulder" in coords:
                            angle = self._calculate_angle_3d(
                                coords["left_shoulder"],
                                coords["left_wrist"],
                                coords["left_elbow"]
                            )
                            angles["left_wrist"] = angle
            except Exception as e:
                logger.debug(f"Left wrist angle error: {e}")
                
        except Exception as e:
            logger.error(f"Error computing angles: {e}")
        
        # CONSOLIDATE BILATERAL ANGLES - Add averaged versions for missing keys
        # This fixes the issue where exercises look for "knee" but only "right_knee"/"left_knee" exist
        
        # Knee: average right and left knee angles
        if "right_knee" in angles and "left_knee" in angles:
            angles["knee"] = (angles["right_knee"] + angles["left_knee"]) / 2
            logger.debug(f"Consolidated knee angle: {angles['knee']:.1f}° (right={angles['right_knee']:.1f}°, left={angles['left_knee']:.1f}°)")
        elif "right_knee" in angles:
            angles["knee"] = angles["right_knee"]
        elif "left_knee" in angles:
            angles["knee"] = angles["left_knee"]
        
        # Hip: Handle BOTH abduction and flexion angles
        # Consolidate hip abduction angles (lateral angle measurement)
        if "right_hip_abduction" in angles and "left_hip_abduction" in angles:
            angles["hip_abduction"] = (angles["right_hip_abduction"] + angles["left_hip_abduction"]) / 2
            logger.debug(f"Consolidated hip abduction angle: {angles['hip_abduction']:.1f}° (right={angles['right_hip_abduction']:.1f}°, left={angles['left_hip_abduction']:.1f}°)")
        elif "right_hip_abduction" in angles:
            angles["hip_abduction"] = angles["right_hip_abduction"]
        elif "left_hip_abduction" in angles:
            angles["hip_abduction"] = angles["left_hip_abduction"]
        
        # Consolidate hip flexion angles (shoulder-hip-knee angle measurement)
        if "right_hip_flexion" in angles and "left_hip_flexion" in angles:
            angles["hip_flexion"] = (angles["right_hip_flexion"] + angles["left_hip_flexion"]) / 2
            logger.debug(f"Consolidated hip flexion angle: {angles['hip_flexion']:.1f}° (right={angles['right_hip_flexion']:.1f}°, left={angles['left_hip_flexion']:.1f}°)")
        elif "right_hip_flexion" in angles:
            angles["hip_flexion"] = angles["right_hip_flexion"]
        elif "left_hip_flexion" in angles:
            angles["hip_flexion"] = angles["left_hip_flexion"]
        
        # Ankle: average right and left ankle angles
        if "right_ankle" in angles and "left_ankle" in angles:
            angles["ankle"] = (angles["right_ankle"] + angles["left_ankle"]) / 2
        elif "right_ankle" in angles:
            angles["ankle"] = angles["right_ankle"]
        elif "left_ankle" in angles:
            angles["ankle"] = angles["left_ankle"]
        
        # Elbow: average right and left elbow angles
        if "right_elbow" in angles and "left_elbow" in angles:
            angles["elbow"] = (angles["right_elbow"] + angles["left_elbow"]) / 2
        elif "right_elbow" in angles:
            angles["elbow"] = angles["right_elbow"]
        elif "left_elbow" in angles:
            angles["elbow"] = angles["left_elbow"]
        
        # Wrist: average right and left wrist angles
        if "right_wrist" in angles and "left_wrist" in angles:
            angles["wrist"] = (angles["right_wrist"] + angles["left_wrist"]) / 2
        elif "right_wrist" in angles:
            angles["wrist"] = angles["right_wrist"]
        elif "left_wrist" in angles:
            angles["wrist"] = angles["left_wrist"]
        
        return angles
    
    def _calculate_angle_3d(self, point1: tuple, point2: tuple, point3: tuple) -> float:
        """Calculate angle between three points in 3D space"""
        try:
            # Validate inputs
            if not all(isinstance(p, (tuple, list)) and len(p) == 3 for p in [point1, point2, point3]):
                logger.debug(f"Invalid points for angle calculation")
                return 0
            
            # Check for NaN or inf values
            for p, name in [(point1, 'p1'), (point2, 'p2'), (point3, 'p3')]:
                if any(np.isnan(v) or np.isinf(v) for v in p):
                    logger.debug(f"Invalid coordinate in {name}: {p}")
                    return 0
            
            # Vectors from point2 to point1 and point3
            v1 = (point1[0] - point2[0], point1[1] - point2[1], point1[2] - point2[2])
            v2 = (point3[0] - point2[0], point3[1] - point2[1], point3[2] - point2[2])
            
            # Calculate dot product
            dot_product = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
            
            # Calculate magnitudes
            mag1 = (v1[0]**2 + v1[1]**2 + v1[2]**2)**0.5
            mag2 = (v2[0]**2 + v2[1]**2 + v2[2]**2)**0.5
            
            if mag1 < 1e-6 or mag2 < 1e-6:
                logger.debug(f"Zero-length vector: mag1={mag1:.6f}, mag2={mag2:.6f}")
                return 0
            
            # Calculate angle in radians
            cos_angle = dot_product / (mag1 * mag2)
            cos_angle = max(-1, min(1, cos_angle))  # Clamp to [-1, 1]
            angle_rad = np.arccos(cos_angle)
            
            # Convert to degrees
            angle_deg = np.degrees(angle_rad)
            
            # Validate result
            if np.isnan(angle_deg) or np.isinf(angle_deg):
                logger.debug(f"Invalid angle result: {angle_deg}")
                return 0
            
            return angle_deg
            
        except Exception as e:
            logger.error(f"Error calculating angle: {e}")
            return 0
    
    def _calculate_lateral_angle(self, hip_point: tuple, knee_point: tuple) -> float:
        """Calculate lateral angle from vertical for hip abduction/adduction"""
        try:
            # Validate inputs
            if not all(isinstance(p, (tuple, list)) and len(p) == 3 for p in [hip_point, knee_point]):
                logger.debug(f"Invalid points for lateral angle calculation")
                return 0
            
            # Check for NaN or inf values
            for p, name in [(hip_point, 'hip'), (knee_point, 'knee')]:
                if any(np.isnan(v) or np.isinf(v) for v in p):
                    logger.debug(f"Invalid coordinate in {name}: {p}")
                    return 0
            
            # Vector from hip to knee
            hip_to_knee = (
                knee_point[0] - hip_point[0],  # Lateral displacement (X)
                knee_point[1] - hip_point[1]   # Vertical displacement (Y)
            )
            
            # Vertical reference vector (pointing down, positive Y in standard coords)
            # But in image coordinates, Y increases downward
            # When standing normally, knee is below hip, so hip_to_knee[1] > 0
            # We want angle from vertical: 0° = straight down, 90° = horizontal
            
            # Calculate angle using atan2
            # atan2(lateral, vertical) gives us the angle from vertical
            lateral_disp = hip_to_knee[0]  # X displacement (left-right)
            vertical_disp = hip_to_knee[1]  # Y displacement (up-down)
            
            # Magnitude of the vector
            magnitude = np.sqrt(lateral_disp**2 + vertical_disp**2)
            
            if magnitude < 1e-6:
                logger.debug(f"Near-zero magnitude for lateral angle: {magnitude:.6f}")
                return 0
            
            # Calculate angle from vertical using atan2(lateral, vertical)
            # Return absolute value and scale to 0-90 range
            if vertical_disp >= 0:
                # Normal standing position: knee below hip
                angle_rad = np.arctan2(abs(lateral_disp), vertical_disp)
            else:
                # Leg raised: knee above hip (uncommon but possible)
                angle_rad = np.arctan2(abs(lateral_disp), abs(vertical_disp))
            
            # Convert to degrees (0-90 range)
            angle_deg = np.degrees(angle_rad)
            
            # Validate result
            if np.isnan(angle_deg) or np.isinf(angle_deg):
                logger.debug(f"Invalid lateral angle result: {angle_deg}")
                return 0
            
            # Clamp to reasonable range for abduction (0-90 degrees)
            angle_deg = max(0, min(90, angle_deg))
            
            return angle_deg
            
        except Exception as e:
            logger.error(f"Error calculating lateral angle: {e}")
            return 0
    
    def _compute_all_angles(self, coords: Dict) -> Dict:
        """Compute all joint angles"""
        angles = {}
        
        if not ORIGINAL_MODULES_AVAILABLE:
            return angles
        
        try:
            # Elbow flexion/extension
            if coords.get("shoulder") and coords.get("elbow"):
                if coords.get("wrist"):
                    raw_angle = elbow_angle(coords["shoulder"], coords["elbow"], coords["wrist"])
                else:
                    raw_angle = elbow_angle(coords["shoulder"], coords["elbow"], coords["elbow"])
                
                logger.info(f"Elbow angle - raw: {raw_angle}, coords present: shoulder={bool(coords.get('shoulder'))}, elbow={bool(coords.get('elbow'))}, wrist={bool(coords.get('wrist'))}")
                
                if raw_angle > 0:
                    angles["elbow"] = self.smoothers["elbow"].update(raw_angle)
                    angles["elbow_extension"] = angles["elbow"]
                    logger.info(f"Elbow angle computed: {angles['elbow']}")
                else:
                    angles["elbow"] = self.previous_angles.get("elbow", 0)
                    angles["elbow_extension"] = self.previous_angles.get("elbow_extension", 0)
                    logger.info(f"Elbow angle is zero, using previous: {angles['elbow']}")
            
            # Shoulder angles
            if coords.get("hip") and coords.get("shoulder") and coords.get("elbow"):
                # Flexion
                raw_angle = shoulder_flexion_angle(coords["shoulder"], coords["elbow"], coords["hip"])
                angles["shoulder_flexion"] = self.smoothers["shoulder_flexion"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("shoulder_flexion", 0)
                
                # Extension
                raw_angle = shoulder_extension_angle(coords["shoulder"], coords["elbow"], coords["hip"])
                angles["shoulder_extension"] = self.smoothers["shoulder_extension"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("shoulder_extension", 0)
            
            if coords.get("elbow") and coords.get("shoulder") and coords.get("hip"):
                # Abduction/Adduction
                raw_angle = shoulder_abduction_angle(coords["shoulder"], coords["elbow"], coords["hip"])
                angles["shoulder_abduction"] = self.smoothers["shoulder_abduction"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("shoulder_abduction", 0)
                angles["shoulder_adduction"] = self.smoothers["shoulder_adduction"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("shoulder_adduction", 0)
                
                # Horizontal abduction/adduction
                raw_angle = shoulder_horizontal_abduction_angle(coords["shoulder"], coords["elbow"], coords["hip"])
                angles["shoulder_horizontal_abduction"] = self.smoothers["shoulder_horizontal_abduction"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("shoulder_horizontal_abduction", 0)
                
                raw_angle = shoulder_horizontal_adduction_angle(coords["shoulder"], coords["elbow"], coords["hip"])
                angles["shoulder_horizontal_adduction"] = self.smoothers["shoulder_horizontal_adduction"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("shoulder_horizontal_adduction", 0)
                
                # Circumduction
                raw_angle = shoulder_circumduction_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_hip"])
                angles["shoulder_circumduction"] = self.smoothers["shoulder_circumduction"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("shoulder_circumduction", 0)
            
            if coords.get("right_shoulder") and coords.get("right_elbow") and coords.get("right_wrist"):
                # Internal/External rotation
                raw_angle = shoulder_internal_rotation_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_wrist"])
                angles["shoulder_internal_rotation"] = self.smoothers["shoulder_internal_rotation"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("shoulder_internal_rotation", 0)
                
                raw_angle = shoulder_external_rotation_angle(coords["right_shoulder"], coords["right_elbow"], coords["right_wrist"])
                angles["shoulder_external_rotation"] = self.smoothers["shoulder_external_rotation"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("shoulder_external_rotation", 0)
            
            # Knee flexion - using right side
            if coords.get("right_hip") and coords.get("right_knee"):
                if coords.get("right_ankle"):
                    raw_angle = knee_angle(coords["right_hip"], coords["right_knee"], coords["right_ankle"])
                else:
                    raw_angle = knee_angle(coords["right_hip"], coords["right_knee"], coords["right_knee"])
                angles["knee"] = self.smoothers["knee"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("knee", 0)
                logger.info(f"Knee flexion angle computed: {angles['knee']}")
            
            # Hip abduction - using right side
            if coords.get("right_shoulder") and coords.get("right_hip") and coords.get("right_knee"):
                raw_angle = hip_angle(coords["right_shoulder"], coords["right_hip"], coords["right_knee"])
                angles["hip"] = self.smoothers["hip"].update(raw_angle) if raw_angle > 0 else self.previous_angles.get("hip", 0)
                logger.info(f"Hip abduction angle computed: {angles['hip']}")
                
        except Exception as e:
            logging.error(f"Error computing angles: {e}")
        
        return angles
    
    def _track_selected_exercise(self, selected_exercise: str, angles: Dict, motion: Dict, result: Dict) -> Dict:
        """Track a specific exercise (exercise-specific mode)"""
        # Map exercise to angle key (comprehensive mapping for ALL exercises)
        # Keys must match what's actually in the angles dictionary from _compute_angles_basic
        angle_map = {
            # Shoulder exercises (mapped to the actual angle keys stored in angles dict)
            "Shoulder Flexion": ["shoulder_flexion"],
            "Shoulder Extension": ["shoulder_extension"],
            "Shoulder Abduction": ["shoulder_abduction"],
            "Shoulder Adduction": ["shoulder_adduction"],
            "Shoulder Internal Rotation": ["shoulder_internal_rotation"],
            "Shoulder External Rotation": ["shoulder_external_rotation"],
            "Shoulder Horizontal Abduction": ["shoulder_horizontal_abduction"],
            "Shoulder Horizontal Adduction": ["shoulder_horizontal_adduction"],
            "Shoulder Circumduction": ["shoulder_circumduction"],
            
            # Elbow exercises
            "Elbow Flexion": ["elbow"],
            "Elbow Extension": ["elbow"],
            
            # Knee exercises
            "Knee Flexion": ["knee"],
            "Knee Extension": ["knee"],
            
            # Hip exercises - Now with separate abduction and flexion
            "Hip Abduction": ["hip_abduction", "hip"],  # Try abduction first, fallback to hip
            "Hip Flexion": ["hip_flexion", "hip"],      # Try flexion first, fallback to hip
            
            # Squat exercises (all use knee angle)
            "Body Weight Squat": ["knee"],
            "Wall Sit": ["knee"],
            "Sumo Squat": ["knee"],
            "Partial Squat": ["knee"],
            "Squat Hold": ["knee"],
            
            # Ankle exercises (computed from ankle landmarks if available)
            "Ankle Dorsiflexion": ["ankle"],
            "Ankle Plantarflexion": ["ankle"],
            "Ankle Inversion": ["ankle"],
            "Ankle Eversion": ["ankle"],
            "Ankle Circles": ["ankle"],
            
            # Wrist exercises (computed from hand landmarks if available)
            "Wrist Flexion": ["wrist"],
            "Wrist Extension": ["wrist"],
            
            # Neck exercises - CORRECTED to use actual angle keys
            "Neck Flexion": ["neck_flexion"],        # Uses improved neck flexion calculation
            "Neck Extension": ["neck_extension"],    # Uses improved neck extension calculation
            "Neck Rotation": ["neck_rotation"],      # Uses improved neck rotation calculation
            
            # Back exercises (use shoulder as proxy)
            "Back Extension": ["shoulder_extension"],
        }
        
        # Get the most relevant angle for this exercise
        angle_keys = angle_map.get(selected_exercise, [])
        current_angle = 0
        angle_used = None
        
        # Try to find angle for this specific exercise
        for key in angle_keys:
            if key in angles and angles[key] > 0:
                current_angle = angles[key]
                angle_used = key
                logger.info(f"=== Exercise: {selected_exercise} ===")
                logger.info(f"PRIMARY MATCH - Found angle {key}: {current_angle:.1f}")
                break
        
        # Log angle detection for debugging
        if current_angle == 0:
            logger.info(f"=== Exercise: {selected_exercise} ===")
            logger.info(f"Angle keys needed: {angle_keys}")
            logger.info(f"All angles computed: {angles}")
        else:
            logger.info(f"Angle keys needed: {angle_keys}, All angles: {angles}")
        
        # If specific angle not found, try to use any shoulder/joint angle as fallback
        if current_angle == 0 and len(angles) > 0:
            # For shoulder exercises, try to use ANY shoulder angle
            if "shoulder" in selected_exercise.lower():
                # Try all possible shoulder angle keys
                shoulder_keys = ['shoulder_flexion', 'shoulder_extension', 'shoulder_abduction', 
                                'shoulder_adduction', 'shoulder_internal_rotation', 'shoulder_external_rotation',
                                'shoulder_horizontal_abduction', 'shoulder_horizontal_adduction', 'shoulder_circumduction']
                for angle_key in shoulder_keys:
                    if angle_key in angles and angles[angle_key] > 0:
                        current_angle = angles[angle_key]
                        angle_used = angle_key
                        logger.info(f"SHOULDER FALLBACK - Using {angle_key}: {current_angle:.1f}")
                        break
            
            # If still not found, use first available non-zero angle as fallback
            if current_angle == 0:
                for angle_key, angle_val in angles.items():
                    if angle_val > 0:
                        current_angle = angle_val
                        angle_used = angle_key
                        logger.info(f"GENERIC FALLBACK - Using {angle_key}: {current_angle:.1f}")
                        break
        
        # Check if we have angles at all
        if current_angle == 0 and len(angles) == 0:
            # No angles at all - could be no landmarks
            result["posture_message"] = "No clear joint movement detected"
            result["exercise"] = selected_exercise
            result["reps"] = 0
            result["angle"] = 0
            result["quality_score"] = 0
            return result
        
        # Get properly isolated state for this exercise
        state = self.state_manager.get_state(selected_exercise)
        
        logger.debug(f"State for {selected_exercise} before counting: reps={state.get('reps', 0)}, angle={current_angle}")
        
        # Determine exercise type and counting logic
        # Pass motion data so we can validate motion for squat exercises
        reps, posture_msg = self._count_reps_simple(selected_exercise, current_angle, state, motion, angle_used)
        
        # CRITICAL: Persist ALL state fields back to manager - not just a few!
        # The state dict was modified during _count_reps_simple so we need to save it all
        self.state_manager.update_state(selected_exercise, 
            reps=state.get('reps', 0),
            last_angle=state.get('last_angle', 0),
            direction=state.get('direction'),
            counting=state.get('counting'),
            phase=state.get('phase', 'extended'),
            been_above=state.get('been_above', False),
            been_below=state.get('been_below', False),
            direction_set=state.get('direction_set', False),
            peak_angle=state.get('peak_angle', 0),
            valley_angle=state.get('valley_angle', 0),
            exited_since_last=state.get('exited_since_last', True)
        )
        
        logger.debug(f"State for {selected_exercise} after counting: reps={state.get('reps', 0)}, phase={state.get('phase')}")
        
        # Simple quality scoring based on angle range
        quality_score = self._calculate_quality_score(selected_exercise, current_angle)
        
        result.update({
            "exercise": selected_exercise,
            "reps": reps,
            "angle": current_angle,
            "posture_message": posture_msg,
            "quality_score": quality_score,
            "confidence": 0.9,
            "joint_tracked": angle_used
        })
        
        return result
    
    def _count_reps_simple(self, exercise: str, angle: float, state: dict, motion: dict = None, angle_key: str = None) -> tuple:
        """Simple rep counting logic using proper two-phase hysteresis state machine"""
        reps = state['reps']
        
        # Validate angle input
        if angle < 0 or angle > 180:
            logger.warning(f"Unusual angle for {exercise}: {angle}")
        
        # SPECIAL CASE: Static hold exercises
        # Wall Sit and Squat Hold are static holds, not reps
        # They should count hold duration, not reps
        is_static_hold = any(hold_name in exercise for hold_name in ["Wall Sit", "Squat Hold"])
        if is_static_hold:
            # Don't do rep counting for static holds
            posture_msg = f"Hold position (angle: {angle:.0f}°)"
            return reps, posture_msg
        
        # SPECIAL CASE: Ankle Circles
        # Full 360-degree rotation, can't use traditional threshold logic
        is_ankle_circles = "Ankle Circles" in exercise
        if is_ankle_circles:
            # For circles, detect when angle wraps from high value (270+) back to low (0-45)
            # This indicates a complete rotation
            last_angle = state.get('last_angle', 0)
            wrapped = (angle < 45 and last_angle > 180)  # Wrapped around from 270°+ to 0-45°
            
            if wrapped:
                reps += 1
                state['reps'] = reps
                logger.info(f"✅ {exercise}: Rep {reps} counted! (angle wrap: {last_angle:.0f}° → {angle:.0f}°)")
                posture_msg = f"✓ Rep {reps}! (rotation complete)"
            else:
                posture_msg = f"Position: {angle:.0f}°"
            state['last_angle'] = angle
            return reps, posture_msg
        
        # Define angle ranges for rep counting by exercise type
        # These ranges represent the FULL RANGE OF MOTION for the exercise
        exercise_ranges = {
            # Shoulder exercises - realistic movement ranges
            "Shoulder Flexion": (10, 140),        # 10-140° range
            "Shoulder Extension": (10, 60),        # ~10-60° range
            "Shoulder Abduction": (10, 140),      # 10-140° range
            "Shoulder Adduction": (10, 60),       # ~10-60° range
            "Shoulder Internal Rotation": (40, 80), # ~40-80° range
            "Shoulder External Rotation": (10, 50), # ~10-50° range
            
            # Elbow exercises
            "Elbow Flexion": (30, 150),           # 30-150° range (full curl)
            "Elbow Extension": (140, 180),        # 140-180° range
            
            # Knee exercises
            "Knee Flexion": (40, 160),            # 40-160° range
            "Knee Extension": (140, 180),         # 140-180° (straight)
            
            # Hip exercises - EXPANDED RANGES for better detection
            "Hip Abduction": (0, 85),             # 0-85° range (wider to catch all movements)
            "Hip Flexion": (5, 120),              # 5-120° range (wider for all variations)
            
            # Squat exercises - ENLARGED RANGES to include standing and full squat
            "Body Weight Squat": (65, 160),       # 65-160° knee angle (standing ~150-160°, squat ~75-85°)
            "Sumo Squat": (65, 160),              # 65-160° (same as body weight squat)
            "Partial Squat": (100, 160),          # 100-160° (shallow squat, less deep)
            "Wall Sit": (60, 120),                # Static hold at 60-120° range
            "Squat Hold": (65, 110),              # Static hold at 65-110°
            
            # Ankle exercises
            "Ankle Dorsiflexion": (70, 120),      # 70-120° (toes toward shin)
            "Ankle Plantarflexion": (100, 160),   # 100-160° (toes down)
            "Ankle Inversion": (10, 60),          # 10-60° (toes in)
            "Ankle Eversion": (0, 50),            # 0-50° (toes out)
            
            # Wrist exercises
            "Wrist Flexion": (20, 140),           # 20-140° range
            "Wrist Extension": (20, 140),         # 20-140° range
            
            # Neck exercises - IMPROVED RANGES based on new calculation
            "Neck Flexion": (25, 90),             # 25-90° range (widened from 20-85)
            "Neck Extension": (25, 90),           # 25-90° range (widened)
            "Neck Rotation": (15, 85),            # 15-85° range
            
            # Back exercises
            "Back Extension": (10, 80),           # 10-80° range
        }
        
        # Get range for this exercise
        if exercise in exercise_ranges:
            target_min, target_max = exercise_ranges[exercise]
        else:
            # Default range for unknown exercises
            target_min, target_max = 20, 150
        
        # Store original angle for state machine logic
        # Do NOT clamp the angle as it breaks phase machine thresholds
        original_angle = angle
        
        # Initialize phase tracking on FIRST call (detect by checking last_angle)
        # If last_angle is 0 and we haven't moved, this is the first real frame
        if state.get('last_angle', 0) == 0 and state.get('phase') == 'extended':
            # Determine starting phase based on initial angle
            midpoint = (target_min + target_max) / 2
            if angle > midpoint:
                state['phase'] = 'flexed'
            else:
                state['phase'] = 'extended'
            state['last_angle'] = angle
            posture_msg = f"Ready to start (angle: {angle:.0f}°)"
            return reps, posture_msg
        
        # Determine exercise type early so we can use flags throughout
        is_squat_exercise = any(squat_name in exercise for squat_name in ["Squat", "Wall Sit"])
        is_hip_exercise = any(hip_name in exercise for hip_name in ["Hip Abduction", "Hip Flexion"])
        is_extension_exercise = any(ext_name in exercise for ext_name in ["Extension", "Back Extension"])
        is_neck_exercise = any(neck_name in exercise for neck_name in ["Neck Flexion", "Neck Extension", "Neck Rotation"])
        
        # Check if movement is significant enough to process
        # Hip exercises are more lenient (1 degree), others need 2 degrees
        min_angle_delta = 1 if is_hip_exercise else 2
        angle_delta = abs(angle - state.get('last_angle', angle))
        if angle_delta < min_angle_delta:  # Only process significant movements
            posture_msg = f"Position: {angle:.0f}°"
            return reps, posture_msg
        
        # Save the previous angle before updating
        prev_angle = state.get('last_angle', angle)
        state['last_angle'] = angle
        
        # TWO-PHASE HYSTERESIS STATE MACHINE
        # Phase 1: EXTENDED - waiting for flexion/movement
        # Phase 2: FLEXED - waiting for return to extended
        # One complete cycle = ONE REP
        
        # Calculate thresholds using dynamic range calculation
        # For hip and squat exercises, use exercise-specific absolute thresholds; for others use percentage
        range_size = target_max - target_min
        
        if is_hip_exercise:  # Hip exercises
            # Hip exercises: Use percentage-based thresholds like other exercises
            threshold_percent = 0.25  # 25% threshold for hip exercises (more lenient than 20%)
            lower_threshold = target_min + range_size * threshold_percent
            upper_threshold = target_max - range_size * threshold_percent
        elif is_squat_exercise:  # Squat exercises
            # Squat exercises: Use percentage-based thresholds for better adaptability
            threshold_percent = 0.20
            lower_threshold = target_min + range_size * threshold_percent
            upper_threshold = target_max - range_size * threshold_percent
        elif is_neck_exercise:  # Neck exercises
            # Neck exercises: Use wider thresholds since neck motion is smaller
            threshold_percent = 0.30  # 30% threshold (more lenient)
            lower_threshold = target_min + range_size * threshold_percent
            upper_threshold = target_max - range_size * threshold_percent
        elif is_extension_exercise:  # Extension exercises
            # Extension exercises starting near max angle
            # Use wider upper threshold since we can't go much higher
            threshold_percent = 0.30  # 30% threshold
            lower_threshold = target_min + range_size * threshold_percent
            upper_threshold = target_max - range_size * threshold_percent
            
            # SPECIAL: For elbow extension specifically, use asymmetric thresholds
            # because the full extension starting point limits motion range
            if "Elbow Extension" in exercise:
                # Start from near max (160°), go down to ~140°, return to ~160°
                # Lower threshold: 145° (minimum extension)
                # Upper threshold: 170° (can't exceed full extension)
                lower_threshold = 145.0
                upper_threshold = 170.0
        else:
            # Other exercises: Use percentage-based thresholds
            threshold_percent = 0.20
            lower_threshold = target_min + range_size * threshold_percent
            upper_threshold = target_max - range_size * threshold_percent
        
        midpoint = (lower_threshold + upper_threshold) / 2
        
        logger.debug(f"{exercise}: phase={state['phase']}, angle={angle:.1f}°, "
                    f"thresholds=[{lower_threshold:.0f}, {upper_threshold:.0f}]")
        
        # Get motion value with fallback logic for hip exercises
        motion_value = 0
        if motion and angle_key:
            motion_value = motion.get(angle_key, 0)
            
            # For hip exercises, try fallback keys if primary key not found
            if motion_value == 0 and is_hip_exercise:
                # Try alternative motion keys for hip exercises
                motion_value = motion.get("hip", motion.get("hip_abduction", motion.get("hip_flexion", 0)))
        
        # For hip exercises, require motion but with lenient threshold
        # Reduced from 2.0 to 0.8 to better detect real movements
        if is_hip_exercise and motion_value < 0.8:
            # Hip exercise with insufficient motion - don't allow state transitions
            posture_msg = f"Position: {angle:.0f}°"
            state['reps'] = reps
            return reps, posture_msg
        
        if is_squat_exercise and motion_value < 1.0:
            # Squat exercise with insufficient motion - don't allow state transitions
            posture_msg = f"Position: {angle:.0f}°"
            state['reps'] = reps
            return reps, posture_msg
        
        if state['phase'] == 'extended':
            # In extended/rest position - waiting for full movement toward max
            if angle > upper_threshold:  # Past upper threshold = started exercise
                state['phase'] = 'flexed'
                logger.debug(f"{exercise}: Transitioned to FLEXED at {angle:.0f}°")
                posture_msg = f"Good! Moving (angle: {angle:.0f}°)"
            else:
                posture_msg = f"Return to start (angle: {angle:.0f}°)"
        
        elif state['phase'] == 'flexed':
            # In flexed position - waiting to return toward minimum (full range)
            if angle <= lower_threshold:  # Completed full movement back (changed from < to <=)
                # Additional check: only count if there was actual motion
                if not is_squat_exercise or motion_value >= 1.0:
                    reps += 1
                    state['phase'] = 'extended'
                    state['reps'] = reps
                    logger.info(f"✅ {exercise}: Rep {reps} counted! (angle: {angle:.0f}°)")
                    posture_msg = f"✓ Rep {reps}! (angle: {angle:.0f}°)"
                else:
                    posture_msg = f"Return to start (angle: {angle:.0f}°)"
            else:
                posture_msg = f"Return to start (angle: {angle:.0f}°)"
        
        state['reps'] = reps
        return reps, posture_msg


    
    def _calculate_quality_score(self, exercise: str, angle: float) -> float:
        """Calculate quality score for exercise form (0-100)"""
        # Define ideal angle ranges where form is considered good
        quality_ranges = {
            # Shoulder exercises
            "Shoulder Flexion": (60, 120),        # Good form at 60-120°
            "Shoulder Extension": (20, 60),       # Good form at 20-60°
            "Shoulder Abduction": (60, 120),      # Good form at 60-120°
            "Shoulder Adduction": (20, 60),       # Good form at 20-60°
            "Shoulder Internal Rotation": (50, 75), # Good form at 50-75°
            "Shoulder External Rotation": (20, 45), # Good form at 20-45°
            
            # Elbow exercises
            "Elbow Flexion": (60, 140),           # Good form at 60-140°
            "Elbow Extension": (150, 180),        # Good form at 150-180°
            
            # Knee exercises
            "Knee Flexion": (80, 160),            # Good form at 80-160°
            "Knee Extension": (160, 180),         # Good form at 160-180°
            
            # Hip exercises
            "Hip Abduction": (30, 70),            # Good form at 30-70°
            "Hip Flexion": (50, 100),             # Good form at 50-100°
            
            # Squat exercises
            "Body Weight Squat": (80, 110),       # Good form at 80-110° knee
            "Wall Sit": (90, 110),                # Good form at 90-110°
            "Sumo Squat": (80, 110),              # Good form at 80-110°
            "Partial Squat": (110, 130),          # Good form at 110-130°
            "Squat Hold": (80, 100),              # Good form at 80-100°
            
            # Ankle exercises
            "Ankle Dorsiflexion": (90, 120),      # Good form at 90-120°
            "Ankle Plantarflexion": (130, 160),   # Good form at 130-160°
            "Ankle Inversion": (30, 60),          # Good form at 30-60°
            "Ankle Eversion": (20, 45),           # Good form at 20-45°
            "Ankle Circles": (0, 360),            # Any angle is good
            
            # Wrist exercises
            "Wrist Flexion": (60, 140),           # Good form at 60-140°
            "Wrist Extension": (60, 140),         # Good form at 60-140°
            
            # Neck exercises - UPDATED RANGES
            "Neck Flexion": (50, 80),             # Good form at 50-80°
            "Neck Extension": (50, 80),           # Good form at 50-80°
            "Neck Rotation": (40, 80),            # Good form at 40-80°
            
            # Back exercises
            "Back Extension": (30, 80),           # Good form at 30-80°
        }
        
        # Get ideal range for this exercise
        if exercise in quality_ranges:
            ideal_min, ideal_max = quality_ranges[exercise]
        else:
            # Default range
            ideal_min, ideal_max = 40, 140
        
        # Check if this is a squat exercise for penalty purposes
        is_squat_exercise = any(squat_name in exercise for squat_name in ["Squat", "Wall Sit"])
        
        # Quality scoring based on proximity to ideal range
        if ideal_min <= angle <= ideal_max:
            # Within ideal range = perfect form
            return 100
        elif angle < ideal_min:
            # Below ideal range - poor form
            gap = ideal_min - angle
            # Use exercise-specific penalty: 2 points per degree for most exercises, 3 for squats
            penalty = 3 if is_squat_exercise else 2
            return max(0, 100 - gap * penalty)
        else:
            # Above ideal range - over-extended
            gap = angle - ideal_max
            # Use exercise-specific penalty: 2 points per degree for most exercises, 3 for squats
            penalty = 3 if is_squat_exercise else 2
            return max(0, 100 - gap * penalty)
    
    def _auto_detect_exercise(self, angles: Dict, motion: Dict, landmarks, result: Dict) -> Dict:
        """Auto-detect exercise from motion"""
        if not self.active_exercise and self.ml_predictor and self.ml_predictor.is_ready():
            # Use ML to predict exercise
            max_motion_val = max(motion.values()) if motion else 0
            
            if max_motion_val > self.MOTION_THRESHOLD:
                predicted_exercise, confidence = self.ml_predictor.predict(landmarks, confidence_threshold=0.0)
                
                if predicted_exercise and confidence >= self.CONFIDENCE_THRESHOLD:
                    # Validate motion matches prediction
                    if self._validate_exercise_motion(predicted_exercise, motion):
                        self.active_exercise = predicted_exercise
                        logging.info(f"Detected exercise: {predicted_exercise} (confidence: {confidence:.2%})")
        
        # Track active exercise
        if self.active_exercise:
            result = self._track_selected_exercise(self.active_exercise, angles, motion, result)
            
            # Check if exercise should end (no motion)
            angle_map = {
                "Elbow Flexion": "elbow", "Elbow Extension": "elbow_extension",
                "Shoulder Flexion": "shoulder_flexion", "Shoulder Extension": "shoulder_extension",
                "Shoulder Abduction": "shoulder_abduction", "Shoulder Adduction": "shoulder_adduction",
                "Shoulder Internal Rotation": "shoulder_internal_rotation", "Shoulder External Rotation": "shoulder_external_rotation",
                "Shoulder Horizontal Abduction": "shoulder_horizontal_abduction", "Shoulder Horizontal Adduction": "shoulder_horizontal_adduction",
                "Shoulder Circumduction": "shoulder_circumduction", "Knee Flexion": "knee", "Hip Abduction": "hip"
            }
            
            joint = angle_map.get(self.active_exercise)
            if joint and motion.get(joint, 0) < 2:
                # Could implement rest counter here to end exercise
                pass
        
        return result
    
    def _validate_posture(self, exercise: str, angle: float) -> str:
        """Validate posture for specific exercise"""
        posture_rules = {
            # Shoulder exercises
            "Shoulder Flexion": (30, 170, "Raise arm higher"),
            "Shoulder Extension": (0, 60, "Extend arm back more"),
            "Shoulder Abduction": (20, 170, "Raise arm higher"),
            "Shoulder Adduction": (0, 60, "Lower arm more"),
            "Shoulder Internal Rotation": (40, 90, "Rotate arm inward"),
            "Shoulder External Rotation": (40, 90, "Rotate arm outward"),
            
            # Elbow exercises
            "Elbow Flexion": (40, 140, "Bend elbow more"),
            "Elbow Extension": (140, 180, "Straighten arm"),
            
            # Knee exercises
            "Knee Flexion": (50, 150, "Bend knee more"),
            "Knee Extension": (140, 180, "Straighten leg"),
            
            # Hip exercises
            "Hip Abduction": (20, 80, "Move leg higher"),
            "Hip Flexion": (40, 110, "Raise leg higher"),
            
            # Squat exercises
            "Body Weight Squat": (60, 110, "Go lower in squat"),
            "Wall Sit": (80, 110, "Hold position steady"),
            "Sumo Squat": (60, 110, "Go lower in squat"),
            "Partial Squat": (100, 130, "Slight squat motion"),
            "Squat Hold": (70, 100, "Hold squat position"),
            
            # Ankle exercises
            "Ankle Dorsiflexion": (80, 120, "Flex ankle upward"),
            "Ankle Plantarflexion": (100, 160, "Point toes downward"),
            "Ankle Inversion": (20, 60, "Turn sole inward"),
            "Ankle Eversion": (0, 45, "Turn sole outward"),
            "Ankle Circles": (0, 360, "Rotate ankle in circles"),
            
            # Wrist exercises
            "Wrist Flexion": (40, 140, "Flex wrist downward"),
            "Wrist Extension": (40, 140, "Extend wrist upward"),
            
            # Neck exercises
            "Neck Flexion": (20, 60, "Tuck chin to chest"),
            "Neck Extension": (20, 60, "Look upward"),
            "Neck Rotation": (30, 80, "Rotate head side to side"),
            
            # Back exercises
            "Back Extension": (10, 60, "Extend back more"),
        }
        
        if exercise in posture_rules:
            min_angle, max_angle, feedback = posture_rules[exercise]
            if min_angle <= angle <= max_angle:
                return "Good form"
            elif angle < min_angle:
                return f"{feedback}"
            else:
                return "Reduce extension"
        
        return "Good form"
    
    def _validate_exercise_motion(self, exercise: str, motion: Dict) -> bool:
        """Validate that motion matches the predicted exercise"""
        if exercise == "Knee Flexion":
            knee_motion = motion.get('knee', 0)
            shoulder_motion = max(motion.get(key, 0) for key in motion if 'shoulder' in key)
            elbow_motion = motion.get('elbow', 0)
            return knee_motion >= 10 and shoulder_motion < 2 and elbow_motion < 2
        
        elif exercise == "Elbow Flexion":
            elbow_motion = motion.get('elbow', 0)
            shoulder_motion = max(motion.get(key, 0) for key in motion if 'shoulder' in key)
            knee_motion = motion.get('knee', 0)
            return elbow_motion >= 8 and elbow_motion > shoulder_motion and knee_motion < 3
        
        elif exercise in self.SHOULDER_EXERCISES:
            shoulder_motion = max(motion.get(key, 0) for key in motion if 'shoulder' in key)
            elbow_motion = motion.get('elbow', 0)
            knee_motion = motion.get('knee', 0)
            return shoulder_motion >= 8 and shoulder_motion > elbow_motion and knee_motion < 3
        
        return False
    
    def reset_exercise(self):
        """Reset the current exercise tracking"""
        self.active_exercise = None
        self.prediction_buffer = []
        
        # Reset rep counters
        if ORIGINAL_MODULES_AVAILABLE:
            for counter in self.rep_counters.values():
                if hasattr(counter, 'reset'):
                    counter.reset()
    
    def get_available_exercises(self) -> List[str]:
        """Get list of available exercises"""
        return self.ALL_EXERCISES.copy()
    
    def get_current_landmarks(self) -> Optional[Dict]:
        """Get current pose landmarks"""
        return self.current_landmarks
    
    def update_rep_count(self, is_rep: bool) -> int:
        """Update repetition count based on ML detection"""
        if is_rep and not hasattr(self, 'last_rep_state'):
            self.rep_count += 1
            self.last_rep_state = True
            return self.rep_count
        elif not is_rep:
            self.last_rep_state = False
        return self.rep_count
    
    def get_current_angle(self, landmarks: Dict, exercise_type: str) -> float:
        """Get current exercise angle based on exercise type"""
        if not landmarks:
            return 0.0
            
        try:
            if 'squat' in exercise_type.lower():
                # Knee angle for squats
                left_knee = self._calculate_angle(landmarks.get(23), landmarks.get(25), landmarks.get(27))
                right_knee = self._calculate_angle(landmarks.get(24), landmarks.get(26), landmarks.get(28))
                return (left_knee + right_knee) / 2 if left_knee and right_knee else 0.0
                
            elif 'shoulder' in exercise_type.lower():
                # Shoulder angle for shoulder exercises
                left_shoulder = self._calculate_angle(landmarks.get(11), landmarks.get(13), landmarks.get(15))
                right_shoulder = self._calculate_angle(landmarks.get(12), landmarks.get(14), landmarks.get(16))
                return (left_shoulder + right_shoulder) / 2 if left_shoulder and right_shoulder else 0.0
                
            elif 'elbow' in exercise_type.lower():
                # Elbow angle for elbow exercises
                left_elbow = self._calculate_angle(landmarks.get(11), landmarks.get(13), landmarks.get(15))
                right_elbow = self._calculate_angle(landmarks.get(12), landmarks.get(14), landmarks.get(16))
                return (left_elbow + right_elbow) / 2 if left_elbow and right_elbow else 0.0
                
            elif 'knee' in exercise_type.lower():
                # Knee angle for knee exercises
                left_knee = self._calculate_angle(landmarks.get(23), landmarks.get(25), landmarks.get(27))
                right_knee = self._calculate_angle(landmarks.get(24), landmarks.get(26), landmarks.get(28))
                return (left_knee + right_knee) / 2 if left_knee and right_knee else 0.0
                
            elif 'hip' in exercise_type.lower():
                # Hip angle for hip exercises
                left_hip = self._calculate_angle(landmarks.get(11), landmarks.get(23), landmarks.get(25))
                right_hip = self._calculate_angle(landmarks.get(12), landmarks.get(24), landmarks.get(26))
                return (left_hip + right_hip) / 2 if left_hip and right_hip else 0.0
                
        except Exception as e:
            print(f"Error calculating angle: {e}")
            return 0.0
            
        return 0.0
    
    def _calculate_angle(self, p1, p2, p3) -> Optional[float]:
        """Calculate angle between three points"""
        if not all([p1, p2, p3]):
            return None
            
        try:
            # Calculate vectors
            v1 = np.array([p1.x - p2.x, p1.y - p2.y])
            v2 = np.array([p3.x - p2.x, p3.y - p2.y])
            
            # Calculate angle
            dot_product = np.dot(v1, v2)
            magnitude = np.linalg.norm(v1) * np.linalg.norm(v2)
            
            if magnitude == 0:
                return None
                
            cos_angle = dot_product / magnitude
            angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
            
            return np.degrees(angle)
        except Exception as e:
            print(f"Error in angle calculation: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        if self.pose:
            self.pose.close()
