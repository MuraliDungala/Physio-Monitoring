import argparse
import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report

# ---------------------------------------
# CONFIGURATION
# ---------------------------------------
DATA_FILE = "data/processed_keypoints/external_exercises.csv"
MODEL_PATH = "models/exercise_recognition/exercise_mlp.pkl"

# ---------------------------------------
# LOAD DATA
# ---------------------------------------
def load_data(data_file):
    if not os.path.exists(data_file):
        raise FileNotFoundError("[ERROR] Training data not found")

    df = pd.read_csv(data_file)

    # Expect aggregated features + label
    label_col = "label" if "label" in df.columns else "exercise_label"
    if label_col not in df.columns:
        raise ValueError("[ERROR] Missing label column: expected 'label' or 'exercise_label'")

    X = df.drop(columns=[label_col]).values
    y = df[label_col].values

    return X, y

# ---------------------------------------
# TRAIN MLP MODEL
# ---------------------------------------
def train_mlp(data_file=DATA_FILE, model_path=MODEL_PATH):
    X, y = load_data(data_file)

    # Encode labels
    label_encoder = LabelEncoder()
    y_enc = label_encoder.fit_transform(y)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc,
        test_size=0.2,
        random_state=42,
        stratify=y_enc
    )

    # Feature scaling
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # MLP Classifier (stable config)
    mlp = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        solver="adam",
        max_iter=400,
        random_state=42
    )

    print("[INFO] Training MLP model...")
    mlp.fit(X_train, y_train)

    # Evaluation
    y_pred = mlp.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("\n[SUCCESS] Training completed")
    print(f"[RESULT] Accuracy: {acc * 100:.2f}%\n")
    print(classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_
    ))

    # Save everything needed for inference
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    joblib.dump({
        "model": mlp,
        "scaler": scaler,
        "label_encoder": label_encoder
    }, model_path)

    print(f"\n[SAVED] Model saved at: {model_path}")

# ---------------------------------------
# MAIN
# ---------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MLP exercise recognition model")
    parser.add_argument(
        "--data-file",
        default=DATA_FILE,
        help="Path to training CSV (must include a 'label' column)",
    )
    parser.add_argument(
        "--model-path",
        default=MODEL_PATH,
        help="Path to save trained model",
    )

    args = parser.parse_args()
    train_mlp(args.data_file, args.model_path)
