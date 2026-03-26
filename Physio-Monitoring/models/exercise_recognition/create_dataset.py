import pandas as pd
import os

DATA_FILES = {
    "Knee Flexion": "data/processed_keypoints/knee_flexion.csv",
    "Elbow Flexion": "data/processed_keypoints/elbow_flexion.csv",
    "Shoulder Abduction": "data/processed_keypoints/shoulder_abduction.csv"
}

OUTPUT_FILE = "data/processed_keypoints/exercise_data.csv"

def create_dataset():
    """
    Load raw pose keypoint data from CSV files and create a labeled training dataset.
    Each input file contains 132 features (33 landmarks × 4 attributes: x,y,z,visibility).
    Labels are added to each file, then all are concatenated into a single dataset.
    """
    all_data = []

    for label, filepath in DATA_FILES.items():
        if not os.path.exists(filepath):
            print(f"⚠️ Missing file: {filepath}")
            continue

        if os.path.getsize(filepath) == 0:
            print(f"⚠️ Empty file skipped: {filepath}")
            continue

        df = pd.read_csv(filepath)

        if df.empty:
            print(f"⚠️ No data in file: {filepath}")
            continue

        # Verify that we have exactly 132 features (33 landmarks × 4 attributes)
        if df.shape[1] != 132:
            print(f"⚠️ {label} has {df.shape[1]} features, expected 132. Skipping.")
            continue

        df["label"] = label
        all_data.append(df)

        print(f"[SUCCESS] Loaded {label}: {df.shape} (132 features per sample)")

    if not all_data:
        raise RuntimeError("❌ No valid data files found")

    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n[SUCCESS] Dataset created at: {OUTPUT_FILE}")
    print(f"[INFO] Total samples: {combined_df.shape[0]}")
    print(f"[INFO] Features: {combined_df.shape[1] - 1} (excluding label)")
    print(f"[INFO] Classes: {combined_df['label'].nunique()}")
    print(f"Class distribution:\n{combined_df['label'].value_counts()}")

if __name__ == "__main__":
    create_dataset()
