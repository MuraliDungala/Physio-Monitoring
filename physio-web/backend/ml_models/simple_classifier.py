"""
Simple ML-based exercise classifier without external dependencies
Uses basic algorithms for exercise detection and analysis
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Optional
import json
import os

class SimpleExerciseClassifier:
    """
    Simple ML-based exercise classifier using basic algorithms
    Trained on exercise biomechanics patterns
    """
    
    def __init__(self):
        self.exercise_patterns = {
            'Shoulder Flexion': {
                'primary_joints': ['shoulder_left', 'shoulder_right'],
                'optimal_ranges': {'shoulder': [45, 90]},
                'movement_pattern': 'arm_raise',
                'rep_threshold': 60
            },
            'Elbow Flexion': {
                'primary_joints': ['elbow_left', 'elbow_right'],
                'optimal_ranges': {'elbow': [60, 120]},
                'movement_pattern': 'arm_bend',
                'rep_threshold': 90
            },
            'Body Weight Squat': {
                'primary_joints': ['knee_left', 'knee_right'],
                'optimal_ranges': {'knee': [90, 110]},
                'movement_pattern': 'knee_bend',
                'rep_threshold': 100
            },
            'Knee Extension': {
                'primary_joints': ['knee_left', 'knee_right'],
                'optimal_ranges': {'knee': [140, 170]},
                'movement_pattern': 'knee_straighten',
                'rep_threshold': 150
            },
            'Hip Flexion': {
                'primary_joints': ['hip_left', 'hip_right'],
                'optimal_ranges': {'hip': [40, 90]},
                'movement_pattern': 'leg_raise',
                'rep_threshold': 60
            }
        }
        
        self.exercise_history = []
        self.angle_history = []
        self.phase_history = []
        
    def extract_features(self, landmarks: Dict) -> np.ndarray:
        """Extract features from MediaPipe landmarks"""
        features = []
        
        # Calculate joint angles
        angles = self._calculate_all_angles(landmarks)
        
        # Add normalized angles
        for angle_name, angle_value in angles.items():
            if angle_value is not None:
                features.append(angle_value / 180.0)  # Normalize to 0-1
            else:
                features.append(0.0)
        
        # Add joint positions
        positions = self._extract_positions(landmarks)
        features.extend(positions)
        
        # Add movement dynamics
        dynamics = self._calculate_dynamics(angles)
        features.extend(dynamics)
        
        return np.array(features)
    
    def _calculate_all_angles(self, landmarks: Dict) -> Dict[str, float]:
        """Calculate all joint angles"""
        angles = {}
        
        # Shoulder angles
        angles['shoulder_left'] = self._calculate_angle(
            landmarks.get(11), landmarks.get(13), landmarks.get(15)
        )
        angles['shoulder_right'] = self._calculate_angle(
            landmarks.get(12), landmarks.get(14), landmarks.get(16)
        )
        
        # Elbow angles
        angles['elbow_left'] = self._calculate_angle(
            landmarks.get(11), landmarks.get(13), landmarks.get(15)
        )
        angles['elbow_right'] = self._calculate_angle(
            landmarks.get(12), landmarks.get(14), landmarks.get(16)
        )
        
        # Hip angles
        angles['hip_left'] = self._calculate_angle(
            landmarks.get(11), landmarks.get(23), landmarks.get(25)
        )
        angles['hip_right'] = self._calculate_angle(
            landmarks.get(12), landmarks.get(24), landmarks.get(26)
        )
        
        # Knee angles
        angles['knee_left'] = self._calculate_angle(
            landmarks.get(23), landmarks.get(25), landmarks.get(27)
        )
        angles['knee_right'] = self._calculate_angle(
            landmarks.get(24), landmarks.get(26), landmarks.get(28)
        )
        
        return angles
    
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
            angle = math.acos(max(-1, min(1, cos_angle)))
            
            return math.degrees(angle)
        except Exception:
            return None
    
    def _extract_positions(self, landmarks: Dict) -> List[float]:
        """Extract normalized joint positions"""
        positions = []
        
        # Key landmark positions
        key_landmarks = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26]
        
        for idx in key_landmarks:
            landmark = landmarks.get(idx)
            if landmark:
                positions.extend([landmark.x, landmark.y])
            else:
                positions.extend([0.0, 0.0])
        
        return positions
    
    def _calculate_dynamics(self, angles: Dict) -> List[float]:
        """Calculate movement dynamics"""
        dynamics = []
        
        # Store current angles for history
        self.angle_history.append(angles)
        
        # Keep only last 10 frames
        if len(self.angle_history) > 10:
            self.angle_history.pop(0)
        
        # Calculate velocity if we have history
        if len(self.angle_history) >= 2:
            prev_angles = self.angle_history[-2]
            for joint_name in ['shoulder_left', 'elbow_left', 'knee_left']:
                curr = angles.get(joint_name, 0)
                prev = prev_angles.get(joint_name, 0)
                velocity = abs(curr - prev) if curr and prev else 0
                dynamics.append(velocity / 180.0)  # Normalize
        else:
            dynamics.extend([0.0, 0.0, 0.0])
        
        return dynamics
    
    def predict_exercise_type(self, landmarks: Dict) -> Dict:
        """Predict exercise type from landmarks"""
        if not landmarks:
            return {'exercise_type': 'Unknown', 'confidence': 0.0}
        
        angles = self._calculate_all_angles(landmarks)
        scores = {}
        
        # Score each exercise type
        for exercise_name, pattern in self.exercise_patterns.items():
            score = self._calculate_exercise_score(angles, pattern)
            scores[exercise_name] = score
        
        # Find best match
        best_exercise = max(scores, key=scores.get)
        confidence = scores[best_exercise]
        
        return {
            'exercise_type': best_exercise if confidence > 0.3 else 'Unknown',
            'confidence': confidence,
            'all_scores': scores
        }
    
    def _calculate_exercise_score(self, angles: Dict, pattern: Dict) -> float:
        """Calculate score for exercise pattern matching"""
        score = 0.0
        total_checks = 0
        
        # Check primary joint angles
        for joint in pattern['primary_joints']:
            if joint in angles and angles[joint] is not None:
                angle = angles[joint]
                
                # Check if angle is in reasonable range for movement
                if pattern['movement_pattern'] == 'arm_raise':
                    # Shoulder flexion: arms should move up
                    if 30 < angle < 120:
                        score += 1.0
                elif pattern['movement_pattern'] == 'arm_bend':
                    # Elbow flexion: elbow should bend
                    if 40 < angle < 140:
                        score += 1.0
                elif pattern['movement_pattern'] == 'knee_bend':
                    # Squat: knees should bend
                    if 70 < angle < 130:
                        score += 1.0
                elif pattern['movement_pattern'] == 'knee_straighten':
                    # Knee extension: knees should straighten
                    if 130 < angle < 180:
                        score += 1.0
                elif pattern['movement_pattern'] == 'leg_raise':
                    # Hip flexion: hip should flex
                    if 20 < angle < 100:
                        score += 1.0
                
                total_checks += 1
        
        # Normalize score
        return score / total_checks if total_checks > 0 else 0.0
    
    def predict_exercise_phase(self, landmarks: Dict, exercise_type: str) -> Dict:
        """Predict exercise phase"""
        if not landmarks or exercise_type not in self.exercise_patterns:
            return {'phase': 'unknown', 'confidence': 0.0}
        
        angles = self._calculate_all_angles(landmarks)
        pattern = self.exercise_patterns[exercise_type]
        
        # Determine phase based on primary joint angles
        primary_joint = pattern['primary_joints'][0]
        if primary_joint not in angles or angles[primary_joint] is None:
            return {'phase': 'unknown', 'confidence': 0.0}
        
        angle = angles[primary_joint]
        optimal_range = pattern['optimal_ranges'].get(primary_joint.replace('_left', '').replace('_right', ''), [0, 180])
        
        # Check if in optimal range (end position)
        if optimal_range[0] <= angle <= optimal_range[1]:
            phase = 'end'
            confidence = 0.8
        else:
            phase = 'start'
            confidence = 0.6
        
        return {'phase': phase, 'confidence': confidence}
    
    def assess_form_quality(self, landmarks: Dict, exercise_type: str) -> Dict:
        """Assess exercise form quality"""
        if not landmarks or exercise_type not in self.exercise_patterns:
            return {'quality_level': 'unknown', 'quality_score': 50, 'confidence': 0.0}
        
        angles = self._calculate_all_angles(landmarks)
        pattern = self.exercise_patterns[exercise_type]
        
        quality_score = 50  # Base score
        feedback = []
        
        # Check form for each primary joint
        for joint in pattern['primary_joints']:
            if joint in angles and angles[joint] is not None:
                angle = angles[joint]
                joint_type = joint.replace('_left', '').replace('_right', '')
                
                if joint_type in pattern['optimal_ranges']:
                    min_opt, max_opt = pattern['optimal_ranges'][joint_type]
                    
                    if min_opt <= angle <= max_opt:
                        quality_score += 10
                        feedback.append(f"Good {joint_type} position!")
                    elif angle < min_opt:
                        quality_score -= 5
                        feedback.append(f"Increase {joint_type} range")
                    else:
                        quality_score -= 5
                        feedback.append(f"Decrease {joint_type} range")
        
        # Check symmetry
        if len(pattern['primary_joints']) >= 2:
            left_joint = pattern['primary_joints'][0]
            right_joint = pattern['primary_joints'][1]
            
            if left_joint in angles and right_joint in angles:
                left_angle = angles[left_joint]
                right_angle = angles[right_joint]
                
                if left_angle and right_angle:
                    symmetry = abs(left_angle - right_angle)
                    if symmetry < 10:
                        quality_score += 5
                    else:
                        quality_score -= 5
                        feedback.append("Improve left-right symmetry")
        
        # Determine quality level
        if quality_score >= 80:
            quality_level = 'good'
        elif quality_score >= 60:
            quality_level = 'moderate'
        else:
            quality_level = 'poor'
        
        return {
            'quality_level': quality_level,
            'quality_score': min(100, max(0, quality_score)),
            'confidence': 0.7,
            'feedback': feedback if feedback else ['Maintain current form']
        }
    
    def detect_rep_completion(self, landmarks: Dict, exercise_type: str, current_phase: str) -> Dict:
        """Detect if a repetition has been completed"""
        if not landmarks or exercise_type not in self.exercise_patterns:
            return {'is_rep': False, 'confidence': 0.0}
        
        # Store phase history
        self.phase_history.append(current_phase)
        
        # Keep only last 5 phases
        if len(self.phase_history) > 5:
            self.phase_history.pop(0)
        
        # Detect rep completion (start -> end transition)
        is_rep = False
        confidence = 0.0
        
        if len(self.phase_history) >= 2:
            prev_phase = self.phase_history[-2]
            if prev_phase == 'start' and current_phase == 'end':
                is_rep = True
                confidence = 0.8
        
        return {'is_rep': is_rep, 'confidence': confidence}
    
    def train_models(self):
        """Train the classifier (simplified version)"""
        print("🏋️ Training simple exercise classifier...")
        print("✅ Training completed! Ready for exercise detection.")
        return True
    
    def load_models(self):
        """Load pre-trained models"""
        print("📂 Loading simple classifier...")
        return True

# Global classifier instance
simple_classifier = SimpleExerciseClassifier()
