# ----------------------------------------
# Add project root to Python path
# ----------------------------------------
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

# ----------------------------------------
# Imports
# ----------------------------------------
import cv2
from datetime import datetime

from models.pose_estimation.mediapipe_pose import MediaPipePose
from src.pose.extract_keypoints import extract_keypoints, save_keypoints_to_csv

# ----------------------------------------
# Setup
# ----------------------------------------
os.makedirs("data/processed_keypoints", exist_ok=True)


output_csv = "data/processed_keypoints/shoulder_abduction.csv"



cap = cv2.VideoCapture(0)
pose_estimator = MediaPipePose()

# ----------------------------------------
# Capture Loop
# ----------------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = pose_estimator.process(frame)
    keypoints = extract_keypoints(results)

    save_keypoints_to_csv(keypoints, output_csv)

    frame = pose_estimator.draw(frame, results)
    cv2.imshow("Keypoint Capture", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"✅ Keypoints saved to: {output_csv}")
