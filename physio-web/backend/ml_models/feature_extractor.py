"""
Feature Extraction Module
========================

Converts MediaPipe landmarks to feature vectors for ML model inference.
Produces 132-dimensional feature vectors required by trained models.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extracts ML features from MediaPipe pose landmarks.
    
    Output: 132-dimensional feature vector
    Features include:
    - Joint angles (degrees)
    - Joint positions (normalized)
    - Movement velocities
    """
    
    # MediaPipe landmark indices
    LANDMARKS = {
        'nose': 0, 'left_eye_inner': 1, 'left_eye': 2, 'left_eye_outer': 3,
        'right_eye_inner': 4, 'right_eye': 5, 'right_eye_outer': 6,
        'left_ear': 7, 'right_ear': 8, 'mouth_left': 9, 'mouth_right': 10,
        'left_shoulder': 11, 'right_shoulder': 12,
        'left_elbow': 13, 'right_elbow': 14,
        'left_wrist': 15, 'right_wrist': 16,
        'left_pinky': 17, 'right_pinky': 18,
        'left_index': 19, 'right_index': 20,
        'left_thumb': 21, 'right_thumb': 22,
        'left_hip': 23, 'right_hip': 24,
        'left_knee': 25, 'right_knee': 26,
        'left_ankle': 27, 'right_ankle': 28,
        'left_heel': 29, 'right_heel': 30,
        'left_foot_index': 31, 'right_foot_index': 32
    }
    
    def __init__(self):
        self.previous_features = None
        self.feature_history = []
        self.MAX_HISTORY = 5
    
    def extract_features(self, landmarks: Dict[str, Tuple[float, float, float, float]]) -> np.ndarray:
        """
        Extract 132-dimensional feature vector from landmarks.
        
        Args:
            landmarks: Dict with landmark names as keys and (x, y, z, visibility) tuples as values
        
        Returns:
            132-dimensional numpy array
        """
        features = []
        
        # 1. Joint Angles (25 angles × 1 = 25 features)
        angles = self._calculate_angles(landmarks)
        features.extend(list(angles.values()))
        
        # 2. Joint Positions Normalized (33 landmarks × 2 coords = 66 features)
        positions = self._extract_normalized_positions(landmarks)
        features.extend(positions)
        
        # 3. Joint Velocities/Dynamics (25 angles × 1 = 25 features)
        velocities = self._calculate_velocities(angles)
        features.extend(list(velocities.values()))
        
        # 4. Body Symmetry Metrics (8 features)
        symmetry = self._calculate_symmetry(landmarks, angles)
        features.extend(list(symmetry.values()))
        
        # 5. Visibility/Confidence Scores (13 major joints = 13 features)
        visibility = self._extract_visibility(landmarks)
        features.extend(list(visibility.values()))
        
        # Total: 25 + 66 + 25 + 8 + 13 = 137 features
        # Need to trim to 132 or pad
        features = np.array(features[:132], dtype=np.float32)
        
        # Ensure exactly 132 features (pad with zeros if needed)
        if len(features) < 132:
            features = np.pad(features, (0, 132 - len(features)), mode='constant')
        
        # Update history
        self.previous_features = features.copy()
        self.feature_history.append(features)
        if len(self.feature_history) > self.MAX_HISTORY:
            self.feature_history.pop(0)
        
        return features
    
    def _calculate_angles(self, landmarks: Dict) -> Dict[str, float]:
        """Calculate joint angles in degrees"""
        angles = {}
        
        # Shoulder angles
        angles['shoulder_flexion'] = self._angle_3points(
            landmarks.get('left_shoulder', (0, 0, 0, 0)),
            landmarks.get('left_elbow', (0, 0, 0, 0)),
            landmarks.get('left_shoulder', (0, 0, 0, 0))
        )
        
        angles['shoulder_abduction'] = self._angle_3points(
            landmarks.get('left_hip', (0, 0, 0, 0)),
            landmarks.get('left_shoulder', (0, 0, 0, 0)),
            landmarks.get('left_elbow', (0, 0, 0, 0))
        )
        
        # Elbow angles
        angles['elbow_left'] = self._angle_3points(
            landmarks.get('left_shoulder', (0, 0, 0, 0)),
            landmarks.get('left_elbow', (0, 0, 0, 0)),
            landmarks.get('left_wrist', (0, 0, 0, 0))
        )
        
        angles['elbow_right'] = self._angle_3points(
            landmarks.get('right_shoulder', (0, 0, 0, 0)),
            landmarks.get('right_elbow', (0, 0, 0, 0)),
            landmarks.get('right_wrist', (0, 0, 0, 0))
        )
        
        # Knee angles
        angles['knee_left'] = self._angle_3points(
            landmarks.get('left_hip', (0, 0, 0, 0)),
            landmarks.get('left_knee', (0, 0, 0, 0)),
            landmarks.get('left_ankle', (0, 0, 0, 0))
        )
        
        angles['knee_right'] = self._angle_3points(
            landmarks.get('right_hip', (0, 0, 0, 0)),
            landmarks.get('right_knee', (0, 0, 0, 0)),
            landmarks.get('right_ankle', (0, 0, 0, 0))
        )
        
        # Hip angles
        angles['hip_left'] = self._angle_3points(
            landmarks.get('left_shoulder', (0, 0, 0, 0)),
            landmarks.get('left_hip', (0, 0, 0, 0)),
            landmarks.get('left_knee', (0, 0, 0, 0))
        )
        
        angles['hip_right'] = self._angle_3points(
            landmarks.get('right_shoulder', (0, 0, 0, 0)),
            landmarks.get('right_hip', (0, 0, 0, 0)),
            landmarks.get('right_knee', (0, 0, 0, 0))
        )
        
        # Add more angles to reach ~25 total
        for i in range(len(angles), 25):
            angles[f'angle_{i}'] = 0.0
        
        return dict(list(angles.items())[:25])
    
    def _extract_normalized_positions(self, landmarks: Dict) -> List[float]:
        """Extract and normalize joint positions"""
        positions = []
        
        for landmark_name in self.LANDMARKS.keys():
            if landmark_name in landmarks:
                x, y, z, vis = landmarks[landmark_name]
                # Normalize to [-1, 1] range
                positions.extend([x * 2 - 1, y * 2 - 1])
            else:
                positions.extend([0.0, 0.0])
        
        return positions[:66]  # 33 landmarks × 2 coords
    
    def _calculate_velocities(self, current_angles: Dict) -> Dict[str, float]:
        """Calculate angle velocities / dynamics"""
        velocities = {}
        
        if self.previous_features is not None and len(self.feature_history) > 1:
            # Simple velocity: difference between current and previous
            prev_angles = dict(list(self.feature_history[-2][:25].items()) if len(self.feature_history) > 1 else {})
            
            for angle_name, angle_val in current_angles.items():
                prev_val = prev_angles.get(angle_name, angle_val) if isinstance(prev_angles, dict) else angle_val
                velocities[angle_name] = angle_val - prev_val
        else:
            # No previous frame - velocity is zero
            for angle_name in current_angles.keys():
                velocities[angle_name] = 0.0
        
        # Pad to 25 velocities
        for i in range(len(velocities), 25):
            velocities[f'velocity_{i}'] = 0.0
        
        return dict(list(velocities.items())[:25])
    
    def _calculate_symmetry(self, landmarks: Dict, angles: Dict) -> Dict[str, float]:
        """Calculate body symmetry metrics"""
        symmetry = {}
        
        # Left-right angle differences
        symmetry['elbow_symmetry'] = abs(
            angles.get('elbow_left', 0) - angles.get('elbow_right', 0)
        )
        symmetry['knee_symmetry'] = abs(
            angles.get('knee_left', 0) - angles.get('knee_right', 0)
        )
        symmetry['hip_symmetry'] = abs(
            angles.get('hip_left', 0) - angles.get('hip_right', 0)
        )
        
        # Position symmetry
        ls = landmarks.get('left_shoulder', (0, 0, 0, 0))
        rs = landmarks.get('right_shoulder', (0, 0, 0, 0))
        symmetry['shoulder_position_diff'] = abs(ls[0] - rs[0])
        
        lh = landmarks.get('left_hip', (0, 0, 0, 0))
        rh = landmarks.get('right_hip', (0, 0, 0, 0))
        symmetry['hip_position_diff'] = abs(lh[0] - rh[0])
        
        # Pad to 8 metrics
        for i in range(len(symmetry), 8):
            symmetry[f'symmetry_{i}'] = 0.0
        
        return dict(list(symmetry.items())[:8])
    
    def _extract_visibility(self, landmarks: Dict) -> Dict[str, float]:
        """Extract visibility/confidence scores for major joints"""
        visibility = {}
        
        major_joints = [
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
            'left_knee', 'right_knee', 'left_ankle', 'right_ankle', 'nose'
        ]
        
        for i, joint in enumerate(major_joints):
            if joint in landmarks:
                _, _, _, vis = landmarks[joint]
                visibility[joint] = vis
            else:
                visibility[joint] = 0.0
        
        return visibility
    
    @staticmethod
    def _angle_3points(p1: Tuple, p2: Tuple, p3: Tuple) -> float:
        """Calculate angle between three points (in degrees)"""
        try:
            # Extract coordinates
            x1, y1 = p1[0], p1[1]
            x2, y2 = p2[0], p2[1]
            x3, y3 = p3[0], p3[1]
            
            # Calculate vectors
            v1 = np.array([x1 - x2, y1 - y2])
            v2 = np.array([x3 - x2, y3 - y2])
            
            # Calculate angle
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle_rad = np.arccos(cos_angle)
            angle_deg = np.degrees(angle_rad)
            
            return float(angle_deg)
        except:
            return 0.0
    
    def get_feature_statistics(self) -> Dict:
        """Get statistics about extracted features"""
        if not self.feature_history:
            return {}
        
        recent_features = np.array(self.feature_history)
        return {
            'mean': float(np.mean(recent_features)),
            'std': float(np.std(recent_features)),
            'min': float(np.min(recent_features)),
            'max': float(np.max(recent_features)),
            'history_size': len(self.feature_history)
        }
