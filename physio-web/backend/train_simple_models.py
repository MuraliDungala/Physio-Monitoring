"""
Simple ML Model Training - Fast alternative using real data from Physio-Monitoring
Trains models quickly without complex preprocessing
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report

# Path to real training data
PHYSIO_DATA = r"c:\Users\mural\OneDrive\Desktop\Physio-Monitoring\Physio-Monitoring\data\processed_keypoints\external_exercises.csv"
MODEL_DIR = Path(__file__).parent / "ml_models"

def train_models():
    print("[INFO] Loading training data...")
    
    # Load real data from Physio-Monitoring
    if not Path(PHYSIO_DATA).exists():
        print(f"[ERROR] Data file not found: {PHYSIO_DATA}")
        return
    
    df = pd.read_csv(PHYSIO_DATA)
    X = df.drop(columns=['exercise_label']).values
    y = df['exercise_label'].values
    
    print(f"[INFO] Loaded {X.shape[0]} samples with {X.shape[1]} features")
    print(f"[INFO] Exercises: {len(np.unique(y))}")
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_enc = label_encoder.fit_transform(y)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"[INFO] Train samples: {X_train.shape[0]}, Test samples: {X_test.shape[0]}")
    
    results = {}
    
    # Train SVM
    print("\n[1/3] Training SVM...")
    svm = SVC(kernel='rbf', C=100, probability=True, random_state=42)
    svm.fit(X_train_scaled, y_train)
    svm_acc = svm.score(X_test_scaled, y_test)
    results['svm'] = svm_acc
    print(f"[RESULT] SVM Accuracy: {svm_acc:.4f}")
    
    # Train Random Forest
    print("\n[2/3] Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_acc = rf.score(X_test, y_test)
    results['random_forest'] = rf_acc
    print(f"[RESULT] Random Forest Accuracy: {rf_acc:.4f}")
    
    # Train MLP
    print("\n[3/3] Training MLP...")
    mlp = MLPClassifier(hidden_layer_sizes=(128, 64), activation='relu', 
                        solver='adam', max_iter=500, random_state=42)
    mlp.fit(X_train_scaled, y_train)
    mlp_acc = mlp.score(X_test_scaled, y_test)
    results['mlp'] = mlp_acc
    print(f"[RESULT] MLP Accuracy: {mlp_acc:.4f}")
    
    # Select best model
    best_name = max(results, key=results.get)
    print(f"\n[SUMMARY]")
    for name, acc in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name:.<20} {acc:.4f}")
    print(f"\n[BEST] {best_name.upper()} with accuracy {results[best_name]:.4f}")
    
    # Save best model
    MODEL_DIR.mkdir(exist_ok=True)
    
    if best_name == 'svm':
        model_data = {'model': svm, 'scaler': scaler, 'label_encoder': label_encoder, 'type': 'svm'}
    elif best_name == 'random_forest':
        model_data = {'model': rf, 'scaler': None, 'label_encoder': label_encoder, 'type': 'rf'}
    else:
        model_data = {'model': mlp, 'scaler': scaler, 'label_encoder': label_encoder, 'type': 'mlp'}
    
    model_path = MODEL_DIR / f'{best_name}_model.pkl'
    joblib.dump(model_data, model_path)
    print(f"\n[SAVED] Model saved to: {model_path}")
    
    # Also save as default
    default_path = MODEL_DIR / 'exercise_model.pkl'
    joblib.dump(model_data, default_path)
    print(f"[SAVED] Also saved as: {default_path}")
    
    # Print detailed report
    y_pred = model_data['model'].predict(X_test_scaled if best_name != 'random_forest' else X_test)
    print(f"\n[REPORT] Classification Report for {best_name.upper()}:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

if __name__ == "__main__":
    train_models()
