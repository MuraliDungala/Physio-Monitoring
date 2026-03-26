import os
import sys
import numpy as np
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ml.dataset_loader import DatasetLoader

def train_and_evaluate():
    print("=== Multi-Model Training Started ===")
    
    # 1. Load Data
    loader = DatasetLoader()
    X, y = loader.load_all()
    
    if len(X) == 0:
        print("Error: No training data found!")
        return

    # 2. Keypoint Normalization (already checked in loader, but ensuring here)
    # MediaPipe landmarks are 0-1 (mostly), or normalized meters.
    # Our simple scaler will handle distribution shift.

    # 3. Encode Labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    print(f"Classes: {le.classes_}")
    
    # 4. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, random_state=42)
    
    # 5. Scale Features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 6. Define Models
    models = {
        "MLP": MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=1000, random_state=42),
        "SVM": SVC(kernel='rbf', probability=True, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42)
    }
    
    best_name = None
    best_score = 0.0
    best_model = None
    
    results = {}

    print("\n--- Training & Evaluation ---")
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        acc = accuracy_score(y_test, y_pred)
        results[name] = acc
        
        print(f"Accuracy: {acc:.4f}")
        print(classification_report(y_test, y_pred, target_names=le.classes_))
        
        if acc > best_score:
            best_score = acc
            best_name = name
            best_model = model

    print("\n=== Results Summary ===")
    for name, score in results.items():
        print(f"{name}: {score:.4f}")
        
    print(f"\n🏆 Best Model: {best_name} ({best_score:.4f})")
    
    # 7. Save Best Artifact
    output_dir = os.path.join(PROJECT_ROOT, "models", "exercise_recognition")
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, "exercise_model.pkl")
    
    artifact = {
        "model": best_model,
        "scaler": scaler,
        "label_encoder": le,
        "model_type": best_name,
        "accuracy": best_score
    }
    
    joblib.dump(artifact, model_path)
    print(f"\n[OK] Best model saved to: {model_path}")

if __name__ == "__main__":
    train_and_evaluate()
