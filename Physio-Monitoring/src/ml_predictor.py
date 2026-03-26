import os
import joblib
import numpy as np

class MLExercisePredictor:
    """Predict exercise type using trained MLP model"""
    
    def __init__(self, model_path="models/exercise_recognition/exercise_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and preprocessing objects"""
        # Resolve model path: try given path, cwd, and package-relative locations
        candidates = [self.model_path,
                      os.path.join(os.getcwd(), self.model_path),
                      os.path.join(os.path.dirname(__file__), '..', self.model_path),
                      os.path.join(os.path.dirname(__file__), '..', '..', self.model_path)]

        found = None
        for c in candidates:
            c_abs = os.path.abspath(c)
            if os.path.exists(c_abs):
                found = c_abs
                break

        if not found:
            print("[WARNING] Model not found at candidate paths")
            return False
        
        try:
            data = joblib.load(found)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.label_encoder = data["label_encoder"]
            print("[SUCCESS] ML model loaded from " + str(found))
            return True
        except Exception as e:
            print("[ERROR] Error loading model: " + str(e))
            return False
    
    def predict(self, landmarks, confidence_threshold=0.6):
        """
        Predict exercise from landmarks
        
        Args:
            landmarks: MediaPipe landmarks (33 points, each with x, y, z, visibility)
            confidence_threshold: Only return prediction if confidence > threshold
        
        Returns:
            (exercise_name, confidence) or (None, 0) if below threshold
        """
        if self.model is None:
            return None, 0
        
        try:
            # Extract features: flatten landmarks (x, y, z, visibility for each)
            features = []
            for lm in landmarks:
                features.extend([lm.x, lm.y, lm.z, lm.visibility])
            
            features = np.array(features).reshape(1, -1)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get prediction probabilities
            proba = self.model.predict_proba(features_scaled)[0]
            confidence = np.max(proba)
            
            # Only predict if confidence is above threshold
            if confidence < confidence_threshold:
                return None, confidence
            
            # Get the predicted class
            pred_idx = np.argmax(proba)
            exercise_name = self.label_encoder.classes_[pred_idx]
            
            return exercise_name, confidence
        
        except Exception as e:
            print("[ERROR] Prediction error: " + str(e))
            return None, 0
    
    def is_ready(self):
        """Check if model is ready for prediction"""
        return self.model is not None
