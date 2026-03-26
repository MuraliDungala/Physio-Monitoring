"""
ML Inference Integration for Web Backend
Handles all ML-based predictions and inference requests
"""

import numpy as np
import logging
from typing import Dict, List, Optional
from ml_models.advanced_classifier import advanced_classifier

logger = logging.getLogger(__name__)


class MLInferenceService:
    """Manages ML inference requests for the web backend"""
    
    def __init__(self):
        self.classifier = advanced_classifier
        self.request_count = 0
        self.error_count = 0
    
    def classify_exercise(
        self,
        features: np.ndarray,
        biomechanics_info: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Classify exercise from features
        
        Args:
            features: 132-dimensional feature array
            biomechanics_info: Optional biomechanics context
            user_id: Optional user ID for logging
        
        Returns:
            Classification result with confidence
        """
        try:
            self.request_count += 1
            
            # Validate input
            if features is None:
                raise ValueError("Features cannot be None")
            
            features = np.array(features).reshape(1, -1)
            if features.shape[1] != 132:
                raise ValueError(f"Expected 132 features, got {features.shape[1]}")
            
            # Get prediction
            result = self.classifier.predict(features, biomechanics_info)
            
            # Add metadata
            result['request_id'] = self.request_count
            result['user_id'] = user_id
            
            logger.info(f"Prediction: {result['exercise']} (confidence: {result['confidence']:.2f})")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Classification error: {e}")
            return {
                'exercise': 'Unknown',
                'confidence': 0.0,
                'method': 'ERROR',
                'error': str(e),
                'request_id': self.request_count
            }
    
    def batch_classify(
        self,
        features_list: List[np.ndarray],
        biomechanics_list: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """Classify multiple feature sets"""
        results = []
        
        for i, features in enumerate(features_list):
            biomech = biomechanics_list[i] if biomechanics_list else None
            result = self.classify_exercise(features, biomech)
            results.append(result)
        
        return results
    
    def get_classifier_info(self) -> Dict:
        """Get classifier metadata"""
        return {
            'status': 'ready' if self.classifier.is_ready else 'not_ready',
            'models': self.classifier.models.keys(),
            'total_requests': self.request_count,
            'error_count': self.error_count,
            'confidence_threshold': self.classifier.confidence_threshold,
            'num_classes': len(self.classifier.label_encoders.get('RandomForest', {}).classes_) 
                          if self.classifier.label_encoders else 0
        }
    
    def adjust_confidence_threshold(self, threshold: float) -> bool:
        """Adjust confidence threshold for fallback logic"""
        try:
            self.classifier.set_confidence_threshold(threshold)
            logger.info(f"Confidence threshold updated to {threshold:.2f}")
            return True
        except Exception as e:
            logger.error(f"Failed to update threshold: {e}")
            return False


# Global instance
ml_service = MLInferenceService()


def get_ml_service() -> MLInferenceService:
    """Get ML service instance for dependency injection"""
    return ml_service
