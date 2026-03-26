import joblib
import numpy as np
from collections import deque, Counter

class ExercisePredictor:
    """
    Real ML-based, windowed exercise predictor
    Used ONLY for classification, not rep counting
    """

    def __init__(self, model_path="models/exercise_mlp.pkl",
                 window_size=30, history_size=5):
        self.model, self.scaler = joblib.load(model_path)

        self.window_size = window_size
        self.feature_window = []
        self.pred_history = deque(maxlen=history_size)

    def predict_window(self, features):
        """
        features: list of feature vectors
        Example per frame: [elbow_angle, shoulder_angle, knee_angle, hip_angle]
        """

        self.feature_window.extend(features)

        # Wait for full window
        if len(self.feature_window) < self.window_size:
            return None, 0.0

        # Aggregate window (mean features)
        window_np = np.array(self.feature_window)
        mean_features = np.mean(window_np, axis=0)

        self.feature_window.clear()

        # Scale + predict
        X = self.scaler.transform([mean_features])
        probs = self.model.predict_proba(X)[0]

        idx = np.argmax(probs)
        pred = self.model.classes_[idx]
        confidence = probs[idx]

        # History voting (extra stability)
        self.pred_history.append(pred)
        final_pred = Counter(self.pred_history).most_common(1)[0][0]

        return final_pred, confidence
