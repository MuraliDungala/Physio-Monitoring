"""
Train and save SVM model specifically.
"""
import os
import sys
import numpy as np
import joblib
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Physio-Monitoring"))

from src.ml.dataset_loader import DatasetLoader

def train_and_save_svm():
    print("=" * 80)
    print("SVM MODEL TRAINING AND SAVING")
    print("=" * 80)
    
    # 1. Load Data
    print("\n[1/4] Loading data...")
    loader = DatasetLoader()
    X, y = loader.load_all()
    
    if len(X) == 0:
        print("Error: No training data found!")
        return

    print(f"✓ Loaded {len(X)} samples")
    
    # 2. Encode Labels
    print("\n[2/4] Encoding labels...")
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    print(f"✓ Classes: {le.classes_}")
    
    # 3. Split Data
    print("\n[3/4] Splitting and scaling data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print(f"✓ Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
    
    # 4. Train SVM
    print("\n[4/4] Training SVM...")
    svm = SVC(kernel='rbf', probability=True, random_state=42)
    svm.fit(X_train_scaled, y_train)
    
    y_pred = svm.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"✓ SVM Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # Save Model
    output_dir = os.path.join(PROJECT_ROOT, "Physio-Monitoring", "models", "exercise_recognition")
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n[DEBUG] Output directory: {output_dir}")
    
    model_path = os.path.join(output_dir, "exercise_svm.pkl")
    
    artifact = {
        "model": svm,
        "scaler": scaler,
        "label_encoder": le,
        "model_type": "SVM",
        "accuracy": acc
    }
    
    joblib.dump(artifact, model_path)
    print(f"\n✅ SVM model saved to: {model_path}")

if __name__ == "__main__":
    train_and_save_svm()
