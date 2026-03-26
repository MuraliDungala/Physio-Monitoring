import csv
import os

NUM_LANDMARKS = 33

def extract_keypoints(results):
    keypoints = []

    if results.pose_landmarks:
        for lm in results.pose_landmarks.landmark:
            keypoints.extend([lm.x, lm.y, lm.z, lm.visibility])
    else:
        keypoints = [0.0] * (NUM_LANDMARKS * 4)

    return keypoints


def save_keypoints_to_csv(keypoints, file_path):
    """
    Safely save keypoints to CSV (Windows-friendly)
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file_exists = os.path.exists(file_path)

    # Open, write, close immediately (safe)
    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        if not file_exists:
            header = []
            for i in range(NUM_LANDMARKS):
                header += [f"x{i}", f"y{i}", f"z{i}", f"v{i}"]
            writer.writerow(header)

        writer.writerow(keypoints)
