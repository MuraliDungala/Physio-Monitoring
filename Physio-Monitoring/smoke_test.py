import mediapipe as mp
print('mp.solutions exists:', hasattr(mp, 'solutions'))
# instantiate and close Pose to ensure MediaPipe runtime is usable
p = mp.solutions.pose.Pose()
p.close()

from src.ml_predictor import MLExercisePredictor
pred = MLExercisePredictor()
print('ML model loaded:', pred.is_ready())
