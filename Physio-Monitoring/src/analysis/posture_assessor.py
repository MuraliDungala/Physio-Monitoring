"""
Enhanced Posture Assessment Model
Comprehensive rule-based system for evaluating exercise correctness.

Rules are based on:
- Joint alignment (landmark visibility)
- Body symmetry (left-right balance)
- Motion isolation (preventing compensatory movements)
- Range of motion (ROM) compliance
"""

import math
import numpy as np


class PostureAssessor:
    """
    Evaluates exercise posture correctness using rule-based biomechanical checks.
    """
    
    # Visibility threshold - must be confident in landmark detection
    VISIBILITY_THRESHOLD = 0.5
    
    # Angle thresholds for different body alignments
    MAX_SHOULDER_TILT = 15  # degrees - shoulder height difference
    MAX_HIP_TILT = 15       # degrees - hip height difference
    MAX_SPINE_TILT = 20     # degrees - spine lean from vertical
    
    def __init__(self):
        self.prev_angles = {}
        self.angle_history = []
        self.max_history_size = 20
    
    def assess_elbow_flexion(self, landmarks, angles):
        """
        Assess elbow flexion posture correctness.
        
        Rules:
        - Shoulder must stay relatively still (no large movements)
        - Arm must move vertically (no side-to-side motion)
        - Upper arm should remain parallel to body
        
        Returns:
            (posture_correct: bool, feedback: str, score: 0-100)
        """
        issues = []
        
        # Check visibility of key joints
        if not self._check_visibility(landmarks, [11, 13, 15]):  # shoulders, elbows, wrists
            return False, "Cannot detect arm position clearly", 0
        
        # Check shoulder stability
        shoulder_tilt = self._calculate_shoulder_tilt(landmarks)
        if shoulder_tilt > self.MAX_SHOULDER_TILT:
            issues.append("Shoulder uneven - keep shoulders level")
        
        # Check body stability (hip should be relatively stable)
        hip_tilt = self._calculate_hip_tilt(landmarks)
        if hip_tilt > self.MAX_HIP_TILT:
            issues.append("Hips unstable - keep core engaged")
        
        # Check for elbow drift (arm should move vertically, not sideways)
        elbow_drift = self._calculate_elbow_drift(landmarks)
        if elbow_drift > 30:
            issues.append("Elbow drifting sideways - keep arm aligned")
        
        # Calculate score
        score = self._calculate_posture_score(len(issues))
        
        if issues:
            return False, " | ".join(issues), score
        else:
            return True, "Good posture - continue", 100
    
    def assess_shoulder_abduction(self, landmarks, angles):
        """
        Assess shoulder abduction posture correctness.
        
        Rules:
        - Both shoulders must lift equally (symmetry)
        - Elbows should stay extended (not bending)
        - Torso should stay upright (no leaning)
        
        Returns:
            (posture_correct: bool, feedback: str, score: 0-100)
        """
        issues = []
        
        # Check visibility
        if not self._check_visibility(landmarks, [11, 12, 13, 14]):  # Both shoulders and elbows
            return False, "Cannot detect shoulder position clearly", 0
        
        # Check shoulder symmetry (both should lift equally)
        shoulder_symmetry = self._calculate_shoulder_symmetry(landmarks)
        if shoulder_symmetry > 20:
            issues.append("Shoulders not even - raise both equally")
        
        # Check if torso is leaning
        spine_tilt = self._calculate_spine_tilt(landmarks)
        if spine_tilt > self.MAX_SPINE_TILT:
            issues.append("Leaning sideways - keep torso upright")
        
        # Check hip stability
        hip_tilt = self._calculate_hip_tilt(landmarks)
        if hip_tilt > self.MAX_HIP_TILT:
            issues.append("Hips unstable - engage core")
        
        score = self._calculate_posture_score(len(issues))
        
        if issues:
            return False, " | ".join(issues), score
        else:
            return True, "Perfect shoulder alignment", 100
    
    def assess_knee_flexion(self, landmarks, angles):
        """
        Assess knee flexion posture correctness.
        
        Rules:
        - Knee must track over toes (no inward/outward drift)
        - Trunk should stay upright
        - Weight should be distributed evenly
        
        Returns:
            (posture_correct: bool, feedback: str, score: 0-100)
        """
        issues = []
        
        # Check visibility of relevant joints
        if not self._check_visibility(landmarks, [23, 24, 25, 26]):  # hips and knees
            return False, "Cannot detect leg position clearly", 0
        
        # Check trunk alignment
        spine_tilt = self._calculate_spine_tilt(landmarks)
        if spine_tilt > self.MAX_SPINE_TILT:
            issues.append("Leaning forward - keep back straight")
        
        # Check knee alignment (left knee should be over left ankle)
        left_knee_alignment = self._calculate_knee_alignment(landmarks, "left")
        if left_knee_alignment > 20:
            issues.append("Left knee drifting - keep over toes")
        
        # Check right knee alignment
        right_knee_alignment = self._calculate_knee_alignment(landmarks, "right")
        if right_knee_alignment > 20:
            issues.append("Right knee drifting - keep over toes")
        
        # Check weight distribution (hips should stay level)
        hip_tilt = self._calculate_hip_tilt(landmarks)
        if hip_tilt > self.MAX_HIP_TILT:
            issues.append("Weight uneven - distribute equally")
        
        score = self._calculate_posture_score(len(issues))
        
        if issues:
            return False, " | ".join(issues), score
        else:
            return True, "Good knee tracking", 100
    
    def assess_hip_abduction(self, landmarks, angles):
        """
        Assess hip abduction posture correctness.
        
        Rules:
        - Raised leg should stay in line with body
        - Trunk should not lean sideways
        - Supporting leg should be stable
        
        Returns:
            (posture_correct: bool, feedback: str, score: 0-100)
        """
        issues = []
        
        # Check visibility
        if not self._check_visibility(landmarks, [11, 12, 23, 24, 25, 26]):
            return False, "Cannot detect full body position", 0
        
        # Check trunk lean (should not lean away from raised leg)
        spine_tilt = self._calculate_spine_tilt(landmarks)
        if spine_tilt > self.MAX_SPINE_TILT:
            issues.append("Leaning sideways - stay upright")
        
        # Check shoulder stability
        shoulder_tilt = self._calculate_shoulder_tilt(landmarks)
        if shoulder_tilt > self.MAX_SHOULDER_TILT:
            issues.append("Shoulders uneven - keep level")
        
        # Check hip stability (supporting side)
        hip_tilt = self._calculate_hip_tilt(landmarks)
        if hip_tilt > self.MAX_HIP_TILT:
            issues.append("Hips not level - strengthen supporting leg")
        
        score = self._calculate_posture_score(len(issues))
        
        if issues:
            return False, " | ".join(issues), score
        else:
            return True, "Controlled hip movement", 100
    
    # ==================== HELPER METHODS ====================
    
    def _check_visibility(self, landmarks, landmark_indices, threshold=None):
        """Check if landmarks are visible enough for analysis"""
        if threshold is None:
            threshold = self.VISIBILITY_THRESHOLD
        
        for idx in landmark_indices:
            if idx >= len(landmarks):
                return False
            if landmarks[idx].visibility < threshold:
                return False
        return True
    
    def _calculate_shoulder_tilt(self, landmarks):
        """Calculate height difference between shoulders (degrees equivalent)"""
        if not self._check_visibility(landmarks, [11, 12]):
            return 0
        
        left_shoulder_y = landmarks[11].y
        right_shoulder_y = landmarks[12].y
        
        # Convert to pixels and estimate angle (rough approximation)
        tilt = abs(left_shoulder_y - right_shoulder_y) * 100  # Scale to degree-like units
        return tilt
    
    def _calculate_hip_tilt(self, landmarks):
        """Calculate tilt of pelvis (hip level)"""
        if not self._check_visibility(landmarks, [23, 24]):
            return 0
        
        left_hip_y = landmarks[23].y
        right_hip_y = landmarks[24].y
        
        tilt = abs(left_hip_y - right_hip_y) * 100
        return tilt
    
    def _calculate_spine_tilt(self, landmarks):
        """Calculate spine tilt from vertical"""
        if not self._check_visibility(landmarks, [11, 23]):
            return 0
        
        shoulder = (landmarks[11].x, landmarks[11].y)
        hip = (landmarks[23].x, landmarks[23].y)
        
        # Calculate angle from vertical
        dx = hip[0] - shoulder[0]
        dy = hip[1] - shoulder[1]
        
        angle = math.degrees(math.atan2(abs(dx), abs(dy)))
        return angle
    
    def _calculate_shoulder_symmetry(self, landmarks):
        """Calculate left-right shoulder symmetry"""
        if not self._check_visibility(landmarks, [11, 12, 13, 14]):
            return 0
        
        # Check if left and right shoulders are at similar heights
        shoulder_diff = abs(landmarks[11].y - landmarks[12].y)
        
        # Check if elbows are at similar heights
        elbow_diff = abs(landmarks[13].y - landmarks[14].y)
        
        symmetry = (shoulder_diff + elbow_diff) * 50
        return symmetry
    
    def _calculate_elbow_drift(self, landmarks):
        """Calculate how much wrist drifts from elbow (side-to-side)"""
        if not self._check_visibility(landmarks, [13, 15]):  # elbow, wrist
            return 0
        
        elbow_x = landmarks[13].x
        wrist_x = landmarks[15].x
        
        # Horizontal drift in normalized units, scaled to degrees-like
        drift = abs(elbow_x - wrist_x) * 100
        return drift
    
    def _calculate_knee_alignment(self, landmarks, side):
        """Calculate knee-to-ankle alignment (frontal plane)"""
        if side == "left":
            knee_idx, ankle_idx = 25, 27
        else:
            knee_idx, ankle_idx = 26, 28
        
        if not self._check_visibility(landmarks, [knee_idx, ankle_idx]):
            return 0
        
        knee_x = landmarks[knee_idx].x
        ankle_x = landmarks[ankle_idx].x
        
        alignment = abs(knee_x - ankle_x) * 100
        return alignment
    
    def _calculate_posture_score(self, num_issues):
        """Convert number of issues to a 0-100 score"""
        if num_issues == 0:
            return 100
        elif num_issues == 1:
            return 75
        elif num_issues == 2:
            return 50
        else:
            return max(0, 25 - (num_issues - 3) * 5)
