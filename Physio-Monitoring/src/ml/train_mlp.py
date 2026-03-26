import os
import sys
import numpy as np
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ml.dataset_loader import DatasetLoader

def train_model():
    print("=== Model Training Started ===")
    
    # 1. Load Data
    loader = DatasetLoader()
    X, y = loader.load_all()
    
    if len(X) == 0:
        print("Error: No training data found!")
        return

    # 2. Encode Labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    print(f"Classes: {le.classes_}")

    # 3. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
    
    # 4. Scale Features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 5. Train Model
    print("Training MLP Classifier...")
    # Using a slightly larger network as we might have more complex data/movements
    model = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        solver="adam",
        max_iter=500,
        random_state=42,
        early_stopping=True
    )
    
    model.fit(X_train_scaled, y_train)
    
    # 6. Evaluate
    print("\n=== Evaluation Results ===")
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    print(f"Train Accuracy: {train_score:.4f}")
    print(f"Test Accuracy:  {test_score:.4f}")
    
    y_pred = model.predict(X_test_scaled)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # 7. Save Artifacts
    output_dir = os.path.join(PROJECT_ROOT, "models", "exercise_recognition")
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, "exercise_mlp.pkl")
    
    # Save dictionary containing all necessary components
    # Using the same structure as MLExercisePredictor expects
    artifact = {
        "model": model,
        "scaler": scaler,
        "label_encoder": le
    }
    
    joblib.dump(artifact, model_path)
    print(f"\n[OK] Model saved to: {model_path}")

if __name__ == "__main__":
    train_model()
