"""
Advanced Exercise Classifier - Production Deployment
Uses trained ML models (RF, MLP, SVM) with hybrid decision fusion
"""

import numpy as np
import joblib
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class AdvancedExerciseClassifier:
    """
    Production-grade classifier using trained ML models
    - RandomForest: 88.79% accuracy (best performer)
    - MLP: 84.77% accuracy
    - SVM: 84.84% accuracy
    - Hybrid fusion with biomechanics fallback
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.is_ready = False
        self.confidence_threshold = 0.65
        
        # Load trained models
        self._load_trained_models()
        
    def _load_trained_models(self):
        """Load pre-trained ML models from disk"""
        model_dir = Path(__file__).parent
        
        model_files = {
            'RandomForest': model_dir / 'exercise_model.pkl',
            'MLP': model_dir / 'exercise_mlp.pkl',
            'SVM': model_dir / 'exercise_svm.pkl',
        }
        
        for model_name, model_path in model_files.items():
            if model_path.exists():
                try:
                    artifact = joblib.load(str(model_path))
                    self.models[model_name] = artifact['model']
                    self.label_encoders[model_name] = artifact['label_encoder']
                    if artifact.get('scaler'):
                        self.scalers[model_name] = artifact['scaler']
                    logger.info(f"✓ Loaded {model_name} - Accuracy: {artifact.get('accuracy', 'N/A')}")
                except Exception as e:
                    logger.warning(f"Failed to load {model_name}: {e}")
            else:
                logger.warning(f"Model file not found: {model_path}")
        
        self.is_ready = len(self.models) > 0
        if self.is_ready:
            logger.info(f"✅ Classifier ready with {len(self.models)} models")
        else:
            logger.error("❌ No models loaded - classifier not ready")
    
    def predict(
        self,
        features: np.ndarray,
        biomechanics_info: Optional[Dict] = None
    ) -> Dict:
        """
        Make prediction using ensemble voting + biomechanics fusion
        
        Args:
            features: Input feature array (132 features)
            biomechanics_info: Optional dict with biomechanics results
                {
                    'exercise': str,
                    'confidence': float 0-1,
                    'quality_score': int 0-100,
                    'posture_valid': bool,
                    'reps_count': int
                }
        
        Returns:
            {
                'exercise': str,
                'confidence': float,
                'method': str ('ML' or 'FALLBACK'),
                'details': dict
            }
        """
        
        if not self.is_ready:
            return {
                'exercise': 'Unknown',
                'confidence': 0.0,
                'method': 'ERROR',
                'details': {'error': 'Classifier not ready'}
            }
        
        features = np.array(features).reshape(1, -1)
        
        # Get ML predictions from all models
        ml_results = self._ensemble_predict(features)
        
        # Hybrid decision logic
        if ml_results['confidence'] >= self.confidence_threshold:
            # High confidence - use ML
            return {
                'exercise': ml_results['prediction'],
                'confidence': float(ml_results['confidence']),
                'method': 'ML_HIGH_CONFIDENCE',
                'details': {
                    'models_used': ml_results['models_used'],
                    'all_predictions': ml_results['all_predictions'],
                    'biomechanics': biomechanics_info
                }
            }
        else:
            # Low confidence - try biomechanics fallback
            if biomechanics_info and biomechanics_info.get('posture_valid'):
                return {
                    'exercise': biomechanics_info['exercise'],
                    'confidence': float(min(ml_results['confidence'], 
                                          biomechanics_info.get('confidence', 0.5))),
                    'method': 'BIOMECHANICS_FALLBACK',
                    'details': {
                        'ml_prediction': ml_results['prediction'],
                        'ml_confidence': ml_results['confidence'],
                        'biomechanics': biomechanics_info
                    }
                }
            else:
                # No valid fallback - return ML prediction with low confidence warning
                return {
                    'exercise': ml_results['prediction'],
                    'confidence': float(ml_results['confidence']),
                    'method': 'ML_LOW_CONFIDENCE',
                    'details': {
                        'warning': 'Low confidence - consider checking biomechanics',
                        'models_used': ml_results['models_used'],
                        'all_predictions': ml_results['all_predictions']
                    }
                }
    
    def _ensemble_predict(self, features: np.ndarray) -> Dict:
        """
        Get predictions from all available models
        Returns average confidence and most likely prediction
        """
        all_predictions = {}
        votes = {}
        confidences = {}
        
        for model_name in ['RandomForest', 'MLP', 'SVM']:
            if model_name not in self.models:
                continue
            
            try:
                model = self.models[model_name]
                le = self.label_encoders[model_name]
                scaler = self.scalers.get(model_name)
                
                # Scale features if needed
                if scaler:
                    features_to_use = scaler.transform(features)
                else:
                    features_to_use = features
                
                # Get prediction and confidence
                pred_encoded = model.predict(features_to_use)[0]
                prediction = le.inverse_transform([pred_encoded])[0]
                
                # Calculate confidence
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(features_to_use)[0]
                    confidence = float(np.max(proba))
                else:
                    confidence = 1.0
                
                all_predictions[model_name] = {
                    'prediction': prediction,
                    'confidence': confidence
                }
                
                # Vote counting
                if prediction not in votes:
                    votes[prediction] = 0
                    confidences[prediction] = []
                
                votes[prediction] += 1
                confidences[prediction].append(confidence)
                
            except Exception as e:
                logger.warning(f"Error with {model_name}: {e}")
        
        # Determine best prediction
        if not votes:
            return {
                'prediction': 'Unknown',
                'confidence': 0.0,
                'models_used': [],
                'all_predictions': all_predictions
            }
        
        best_prediction = max(votes, key=votes.get)
        avg_confidence = np.mean(confidences[best_prediction])
        
        return {
            'prediction': best_prediction,
            'confidence': float(avg_confidence),
            'models_used': list(self.models.keys()),
            'all_predictions': all_predictions
        }
    
    def set_confidence_threshold(self, threshold: float):
        """Adjust confidence threshold for fallback switching"""
        if not (0.0 <= threshold <= 1.0):
            raise ValueError("Threshold must be between 0.0 and 1.0")
        self.confidence_threshold = threshold
        logger.info(f"Confidence threshold set to {threshold:.2f}")
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        le = self.label_encoders.get('RandomForest')
        num_classes = len(le.classes_) if le else 0
        
        return {
            'is_ready': self.is_ready,
            'models_loaded': list(self.models.keys()),
            'confidence_threshold': self.confidence_threshold,
            'num_features': 132,
            'num_classes': num_classes,
            'classes': list(le.classes_) if le else []
        }


# Global instance for app.py
advanced_classifier = AdvancedExerciseClassifier()


if __name__ == "__main__":
    # Test the classifier
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "=" * 80)
    print("ADVANCED EXERCISE CLASSIFIER - DEPLOYMENT TEST")
    print("=" * 80)
    
    clf = AdvancedExerciseClassifier()
    info = clf.get_model_info()
    
    print(f"\n✅ Classifier Status: {'Ready' if info['is_ready'] else 'Not Ready'}")
    print(f"   Models: {', '.join(info['models_loaded'])}")
    print(f"   Features: {info['num_features']}")
    print(f"   Exercises: {len(info['classes'])}")
    
    if info['is_ready']:
        # Test with random features
        test_features = np.random.randn(132)
        result = clf.predict(test_features)
        
        print(f"\n📊 Test Prediction:")
        print(f"   Exercise: {result['exercise']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Method: {result['method']}")
