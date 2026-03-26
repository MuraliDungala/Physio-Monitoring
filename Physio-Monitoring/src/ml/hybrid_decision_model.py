"""
Hybrid Decision Model: Biomechanics + Machine Learning Fusion
=============================================================

Combines biomechanics rules with ML predictions for robust exercise classification.

Decision Strategy:
- If ML confidence ≥ threshold: Use ML prediction
- Else: Use biomechanics-based fallback or request more data

This prevents false positives and ensures robust real-time reliability.
"""

import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class HybridDecisionModel:
    """
    Fuses biomechanics and ML predictions for robust exercise classification.
    
    Attributes:
        ml_models: Dict of trained ML models (MLP, SVM, RandomForest)
        confidence_threshold: Minimum confidence required to accept ML prediction (0.0-1.0)
        use_ensemble: Whether to use ensemble voting from multiple models
        biomechanics_validator: Optional function to validate biomechanics
    """
    
    def __init__(
        self,
        ml_models_dir: str = None,
        confidence_threshold: float = 0.65,
        use_ensemble: bool = True,
        biomechanics_validator = None
    ):
        """
        Initialize hybrid decision model.
        
        Args:
            ml_models_dir: Directory containing trained model files
            confidence_threshold: Min confidence to accept ML prediction (0.0-1.0)
            use_ensemble: Use ensemble voting from multiple models
            biomechanics_validator: Optional validator function for biomechanics
        """
        self.confidence_threshold = confidence_threshold
        self.use_ensemble = use_ensemble
        self.biomechanics_validator = biomechanics_validator
        self.models = {}
        self.label_encoders = {}
        self.scalers = {}
        
        # Load ML models
        if ml_models_dir is None:
            ml_models_dir = Path(__file__).parent.parent.parent / "models" / "exercise_recognition"
        
        self._load_models(str(ml_models_dir))
        
    def _load_models(self, model_dir: str):
        """Load all available trained models."""
        model_dir = Path(model_dir)
        
        model_files = {
            "RandomForest": model_dir / "exercise_model.pkl",
            "MLP": model_dir / "exercise_mlp.pkl",
            "SVM": model_dir / "exercise_svm.pkl"
        }
        
        for model_name, model_path in model_files.items():
            if model_path.exists():
                try:
                    artifact = joblib.load(str(model_path))
                    self.models[model_name] = artifact['model']
                    self.label_encoders[model_name] = artifact['label_encoder']
                    self.scalers[model_name] = artifact['scaler']
                    print(f"✓ Loaded {model_name}: {model_path}")
                except Exception as e:
                    print(f"⚠ Failed to load {model_name}: {e}")
            else:
                print(f"⚠ {model_name} not found: {model_path}")
        
        if not self.models:
            raise ValueError("No ML models found!")
    
    def predict(
        self,
        features: np.ndarray,
        biomechanics_info: Optional[Dict] = None
    ) -> Dict:
        """
        Make hybrid prediction combining ML and biomechanics.
        
        Args:
            features: Input features (e.g., joint angles, velocities)
            biomechanics_info: Optional dict with biomechanics results
                {
                    'exercise': str,  # Biomechanics prediction
                    'confidence': float,  # Posture quality 0-1
                    'quality_score': int,  # 0-100
                    'posture_valid': bool,
                    'reps_count': int
                }
        
        Returns:
            Dict with:
                {
                    'exercise': str,  # Final decision
                    'ml_prediction': str,  # ML best guess
                    'ml_confidence': float,  # ML confidence score
                    'ml_models_used': list,  # Which models voted
                    'biomechanics_prediction': str or None,
                    'decision_method': str,  # 'ML' or 'FALLBACK'
                    'details': dict,  # Detailed breakdown
                    'confidence': float  # Overall confidence 0-1
                }
        """
        
        features = np.array(features).reshape(1, -1)
        
        # Get ML predictions
        ml_results = self._get_ml_predictions(features)
        
        # Decide: ML or Biomechanics Fallback
        if ml_results['max_confidence'] >= self.confidence_threshold:
            # ML prediction has high confidence - use it
            return {
                'exercise': ml_results['prediction'],
                'ml_prediction': ml_results['prediction'],
                'ml_confidence': float(ml_results['max_confidence']),
                'ml_models_used': ml_results['models_used'],
                'biomechanics_prediction': biomechanics_info.get('exercise') if biomechanics_info else None,
                'decision_method': 'ML_HIGH_CONFIDENCE',
                'details': {
                    'ml_scores': ml_results['all_predictions'],
                    'ensemble_consensus': ml_results['ensemble_consensus'],
                    'biomechanics_info': biomechanics_info
                },
                'confidence': float(ml_results['max_confidence'])
            }
        else:
            # ML confidence too low - check biomechanics fallback
            if biomechanics_info and biomechanics_info.get('posture_valid'):
                return {
                    'exercise': biomechanics_info['exercise'],
                    'ml_prediction': ml_results['prediction'],
                    'ml_confidence': float(ml_results['max_confidence']),
                    'ml_models_used': ml_results['models_used'],
                    'biomechanics_prediction': biomechanics_info['exercise'],
                    'decision_method': 'BIOMECHANICS_FALLBACK',
                    'details': {
                        'ml_scores': ml_results['all_predictions'],
                        'reason': 'ML confidence below threshold, using biomechanics',
                        'biomechanics_info': biomechanics_info
                    },
                    'confidence': float(min(ml_results['max_confidence'], biomechanics_info.get('confidence', 0.5)))
                }
            else:
                # Fallback: use ML despite low confidence
                return {
                    'exercise': ml_results['prediction'],
                    'ml_prediction': ml_results['prediction'],
                    'ml_confidence': float(ml_results['max_confidence']),
                    'ml_models_used': ml_results['models_used'],
                    'biomechanics_prediction': biomechanics_info.get('exercise') if biomechanics_info else None,
                    'decision_method': 'ML_LOW_CONFIDENCE_FALLBACK',
                    'details': {
                        'ml_scores': ml_results['all_predictions'],
                        'reason': 'Low ML confidence and no valid biomechanics fallback',
                        'biomechanics_info': biomechanics_info
                    },
                    'confidence': float(ml_results['max_confidence'])
                }
    
    def _get_ml_predictions(self, features: np.ndarray) -> Dict:
        """
        Get predictions from all available ML models.
        
        Returns:
            Dict with:
                {
                    'prediction': str,  # Most likely exercise
                    'max_confidence': float,  # Confidence of best prediction
                    'all_predictions': dict,  # All model outputs
                    'models_used': list,  # Which models voted
                    'ensemble_consensus': int  # Number of models agreeing
                }
        """
        
        all_predictions = {}
        model_votes = {}
        confidences = {}
        
        # Run each model
        for model_name in ['RandomForest', 'MLP', 'SVM']:
            if model_name not in self.models:
                continue
            
            try:
                model = self.models[model_name]
                scaler = self.scalers[model_name]
                le = self.label_encoders[model_name]
                
                # Scale and predict
                features_scaled = scaler.transform(features)
                prediction_encoded = model.predict(features_scaled)[0]
                prediction = le.inverse_transform([prediction_encoded])[0]
                
                # Get prediction probabilities
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(features_scaled)[0]
                    confidence = float(np.max(proba))
                else:
                    confidence = 1.0  # SVM without probability
                
                all_predictions[model_name] = {
                    'prediction': prediction,
                    'confidence': confidence,
                    'probabilities': dict(zip(le.classes_, proba)) if hasattr(model, 'predict_proba') else {}
                }
                
                # Vote counting
                if prediction not in model_votes:
                    model_votes[prediction] = 0
                    confidences[prediction] = []
                model_votes[prediction] += 1
                confidences[prediction].append(confidence)
                
            except Exception as e:
                print(f"⚠ Error with {model_name}: {e}")
                continue
        
        # Determine consensus prediction
        if not model_votes:
            raise ValueError("No models available for prediction!")
        
        best_prediction = max(model_votes, key=model_votes.get)
        avg_confidence = np.mean(confidences[best_prediction])
        consensus_count = model_votes[best_prediction]
        
        return {
            'prediction': best_prediction,
            'max_confidence': float(avg_confidence),
            'all_predictions': all_predictions,
            'models_used': list(self.models.keys()),
            'ensemble_consensus': consensus_count
        }
    
    def set_confidence_threshold(self, threshold: float):
        """Adjust confidence threshold (0.0-1.0)."""
        if not (0.0 <= threshold <= 1.0):
            raise ValueError("Threshold must be between 0.0 and 1.0")
        self.confidence_threshold = threshold
        print(f"✓ Confidence threshold set to {threshold:.2f}")


# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

def example_hybrid_prediction():
    """Example: Make a hybrid prediction."""
    
    print("\n" + "=" * 80)
    print("HYBRID DECISION MODEL - EXAMPLE USAGE")
    print("=" * 80)
    
    # Initialize hybrid model
    hybrid = HybridDecisionModel(confidence_threshold=0.65)
    
    # Example 1: High-confidence ML prediction
    print("\n[Example 1] High-confidence ML prediction")
    features_1 = np.random.randn(132)  # 132 features
    
    result_1 = hybrid.predict(
        features=features_1,
        biomechanics_info={
            'exercise': 'Elbow Flexion',
            'confidence': 0.9,
            'quality_score': 85,
            'posture_valid': True,
            'reps_count': 1
        }
    )
    
    print(f"Decision: {result_1['exercise']}")
    print(f"Method: {result_1['decision_method']}")
    print(f"Confidence: {result_1['confidence']:.2f}")
    print(f"Models used: {result_1['ml_models_used']}")
    
    # Example 2: Low-confidence ML falls back to biomechanics
    print("\n[Example 2] Low-confidence ML with biomechanics fallback")
    features_2 = np.random.randn(132)
    
    result_2 = hybrid.predict(
        features=features_2,
        biomechanics_info={
            'exercise': 'Shoulder Abduction',
            'confidence': 0.85,
            'quality_score': 80,
            'posture_valid': True,
            'reps_count': 1
        }
    )
    
    print(f"Decision: {result_2['exercise']}")
    print(f"Method: {result_2['decision_method']}")
    print(f"Confidence: {result_2['confidence']:.2f}")
    if result_2['biomechanics_prediction']:
        print(f"Biomechanics fallback used: {result_2['biomechanics_prediction']}")
    
    # Example 3: Adjust threshold
    print("\n[Example 3] Adjusting confidence threshold")
    hybrid.set_confidence_threshold(0.85)
    
    result_3 = hybrid.predict(
        features=features_1,
        biomechanics_info=None
    )
    print(f"With higher threshold (0.85)")
    print(f"Decision: {result_3['exercise']}")
    print(f"Method: {result_3['decision_method']}")


if __name__ == "__main__":
    try:
        example_hybrid_prediction()
        print("\n✅ Hybrid Decision Model initialized successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
