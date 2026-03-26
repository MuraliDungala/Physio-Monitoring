import numpy as np
import joblib
from collections import deque, Counter

model = joblib.load("models/exercise_mlp.pkl")
scaler = joblib.load("models/scaler.pkl")

WINDOW_SIZE = 30
PRED_HISTORY = deque(maxlen=5)
WINDOW = []

def predict_exercise(feature_vector):
    WINDOW.append(feature_vector)

    if len(WINDOW) < WINDOW_SIZE:
        return None, 0.0

    window_mean = np.mean(WINDOW, axis=0)
    WINDOW.clear()

    X = scaler.transform([window_mean])
    probs = model.predict_proba(X)[0]
    confidence = probs.max()
    pred = model.classes_[probs.argmax()]

    if confidence < 0.6:
        return None, confidence

    PRED_HISTORY.append(pred)
    final_pred = Counter(PRED_HISTORY).most_common(1)[0][0]

    return final_pred, confidence
