"""
Prediction Smoothing and Filtering Module
Stabilizes exercise detection using moving average and confidence thresholds
"""

from collections import deque
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PredictionSmoother:
    """
    Smooths exercise predictions to avoid noise and false detections.
    Uses moving average and majority voting for stable detection.
    """
    
    def __init__(self, window_size: int = 10, confidence_threshold: float = 0.70):
        """
        Initialize prediction smoother.
        
        Args:
            window_size: Number of frames to use for smoothing (default 10)
            confidence_threshold: Minimum confidence to accept prediction (0-1)
        """
        self.window_size = window_size
        self.confidence_threshold = confidence_threshold
        
        # Sliding windows for predictions
        self.prediction_history = deque(maxlen=window_size)  # list of (exercise, confidence)
        self.angle_history = deque(maxlen=window_size)  # list of joint angles
        self.quality_history = deque(maxlen=window_size)  # list of quality scores
        
        # State tracking
        self.current_exercise = None
        self.current_confidence = 0.0
        self.previous_exercise = None
        self.exercise_changed = False
        
        logger.info(f"PredictionSmoother initialized: window={window_size}, threshold={confidence_threshold}")
    
    def update(self, 
               exercise: str, 
               confidence: float, 
               angle: Optional[float] = None,
               quality_score: Optional[float] = None) -> Dict:
        """
        Update smoother with new prediction.
        
        Returns:
            Dict with:
            - exercise: Smoothed exercise name
            - confidence: Smoothed confidence
            - angle: Average angle from window
            - quality: Average quality from window
            - exercise_changed: True if exercise changed from previous
            - is_stable: True if prediction is stable enough to trigger voice
        """
        # Store prediction history
        self.prediction_history.append((exercise, confidence))
        
        if angle is not None:
            self.angle_history.append(angle)
        
        if quality_score is not None:
            self.quality_history.append(quality_score)
        
        # Perform majority voting on predictions
        smoothed_exercise, smoothed_confidence = self._get_majority_prediction()
        
        # Calculate averaged values
        avg_angle = self._get_average_angle()
        avg_quality = self._get_average_quality()
        
        # Detect exercise change
        self.previous_exercise = self.current_exercise
        self.current_exercise = smoothed_exercise
        self.current_confidence = smoothed_confidence
        self.exercise_changed = (self.previous_exercise != self.current_exercise) and (self.previous_exercise is not None)
        
        # Determine if prediction is stable enough to use
        is_stable = self._is_prediction_stable()
        
        logger.debug(f"Prediction: {exercise} ({confidence:.2f}) → Smoothed: {smoothed_exercise} ({smoothed_confidence:.2f}), Stable: {is_stable}")
        
        return {
            "exercise": smoothed_exercise,
            "confidence": smoothed_confidence,
            "angle": avg_angle,
            "quality": avg_quality,
            "exercise_changed": self.exercise_changed,
            "is_stable": is_stable,
            "window_size": len(self.prediction_history),
        }
    
    def _get_majority_prediction(self) -> Tuple[Optional[str], float]:
        """
        Get majority vote prediction from history.
        Returns (exercise_name, confidence)
        """
        if not self.prediction_history:
            return None, 0.0
        
        # Count occurrences of each exercise
        exercise_counts = {}
        exercise_confidences = {}
        
        for exercise, confidence in self.prediction_history:
            if exercise not in exercise_counts:
                exercise_counts[exercise] = 0
                exercise_confidences[exercise] = []
            
            exercise_counts[exercise] += 1
            exercise_confidences[exercise].append(confidence)
        
        # Find most common exercise
        if not exercise_counts:
            return None, 0.0
        
        majority_exercise = max(exercise_counts, key=exercise_counts.get)
        
        # Calculate average confidence for majority exercise
        avg_confidence = sum(exercise_confidences[majority_exercise]) / len(exercise_confidences[majority_exercise])
        
        return majority_exercise, avg_confidence
    
    def _get_average_angle(self) -> Optional[float]:
        """Get average angle from history"""
        if not self.angle_history:
            return None
        
        return sum(self.angle_history) / len(self.angle_history)
    
    def _get_average_quality(self) -> Optional[float]:
        """Get average quality score from history"""
        if not self.quality_history:
            return None
        
        return sum(self.quality_history) / len(self.quality_history)
    
    def _is_prediction_stable(self) -> bool:
        """
        Determine if prediction is stable enough for voice triggering.
        
        Stability criteria:
        1. Confidence >= threshold
        2. Window is at least 50% full
        3. Prediction consistency (majority represents >50% of window)
        """
        if not self.prediction_history or self.current_confidence < self.confidence_threshold:
            return False
        
        # Check if window is filling up
        min_window = max(3, self.window_size // 2)  # Need at least 50% of window or 3 frames
        if len(self.prediction_history) < min_window:
            return False
        
        # Check prediction consistency
        if self.current_exercise:
            count = sum(1 for ex, _ in self.prediction_history if ex == self.current_exercise)
            consistency = count / len(self.prediction_history)
            
            # Require >50% consistency
            if consistency < 0.5:
                return False
        
        return True
    
    def reset(self):
        """Reset the smoother state"""
        self.prediction_history.clear()
        self.angle_history.clear()
        self.quality_history.clear()
        self.current_exercise = None
        self.current_confidence = 0.0
        self.previous_exercise = None
        self.exercise_changed = False
        
        logger.info("PredictionSmoother reset")
    
    def get_state(self) -> Dict:
        """Get current state of smoother"""
        return {
            "current_exercise": self.current_exercise,
            "current_confidence": self.current_confidence,
            "previous_exercise": self.previous_exercise,
            "exercise_changed": self.exercise_changed,
            "window_full": len(self.prediction_history) == self.window_size,
            "window_size": len(self.prediction_history),
        }
