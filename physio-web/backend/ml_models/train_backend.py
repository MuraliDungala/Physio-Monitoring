#!/usr/bin/env python
"""
Backend ML Model Training
Trains exercise classification models for the web backend using real Physio-Monitoring data
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "Physio-Monitoring"))

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Real data path
PHYSIO_DATA = Path(__file__).parent.parent.parent.parent / "Physio-Monitoring" / "data" / "processed_keypoints" / "external_exercises.csv"
MODEL_DIR = Path(__file__).parent

def main():
    """Train backend ML models"""
    
    print("=" * 80)
    print("BACKEND ML MODEL TRAINING")
    print("=" * 80)
    
    # Load data
    print(f"\n[1/6] Loading data from: {PHYSIO_DATA}")
    if not PHYSIO_DATA.exists():
        print(f"[ERROR] Data file not found: {PHYSIO_DATA}")
        return False
    
    df = pd.read_csv(PHYSIO_DATA)
    X = df.drop(columns=['exercise_label']).values
    y = df['exercise_label'].values
    
    print(f"✓ Loaded {X.shape[0]:,} samples with {X.shape[1]} features")
    print(f"✓ Exercises: {len(np.unique(y))}")
    print(f"  Classes: {', '.join(np.unique(y)[:5])}...")
    
    # Preprocessing
    print("\n[2/6] Preprocessing...")
    label_encoder = LabelEncoder()
    y_enc = label_encoder.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"✓ Train: {X_train.shape[0]:,}, Test: {X_test.shape[0]:,}")
    print(f"✓ Features scaled")
    
    models_trained = {}
    
    # Train SVM
    print("\n[3/6] Training SVM...")
    try:
        svm = SVC(kernel='rbf', C=100, gamma='scale', probability=True, random_state=42)
        svm.fit(X_train_scaled, y_train)
        svm_acc = accuracy_score(y_test, svm.predict(X_test_scaled))
        models_trained['svm'] = {'model': svm, 'accuracy': svm_acc, 'scaler': scaler}
        print(f"✓ SVM Accuracy: {svm_acc:.4f} ({svm_acc*100:.2f}%)")
    except Exception as e:
        print(f"✗ SVM training failed: {e}")
    
    # Train Random Forest
    print("\n[4/6] Training Random Forest...")
    try:
        rf = RandomForestClassifier(n_estimators=100, max_depth=20, 
                                   min_samples_split=5, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        rf_acc = accuracy_score(y_test, rf.predict(X_test))
        models_trained['random_forest'] = {'model': rf, 'accuracy': rf_acc, 'scaler': None}
        print(f"✓ Random Forest Accuracy: {rf_acc:.4f} ({rf_acc*100:.2f}%)")
    except Exception as e:
        print(f"✗ Random Forest training failed: {e}")
    
    # Train Gradient Boosting
    print("\n[5/6] Training Gradient Boosting...")
    try:
        gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, 
                                       learning_rate=0.1, random_state=42)
        gb.fit(X_train_scaled, y_train)
        gb_acc = accuracy_score(y_test, gb.predict(X_test_scaled))
        models_trained['gradient_boosting'] = {'model': gb, 'accuracy': gb_acc, 'scaler': scaler}
        print(f"✓ Gradient Boosting Accuracy: {gb_acc:.4f} ({gb_acc*100:.2f}%)")
    except Exception as e:
        print(f"✗ Gradient Boosting training failed: {e}")
    
    if not models_trained:
        print("[ERROR] No models were successfully trained")
        return False
    
    # Save models
    print("\n[6/6] Saving models...")
    
    # Find best model
    best_name = max(models_trained, key=lambda x: models_trained[x]['accuracy'])
    best_model = models_trained[best_name]['model']
    best_accuracy = models_trained[best_name]['accuracy']
    best_scaler = models_trained[best_name]['scaler']
    
    # Save all models
    MODEL_DIR.mkdir(exist_ok=True)
    
    for model_name, model_data in models_trained.items():
        model_obj = model_data['model']
        model_scaler = model_data['scaler']
        acc = model_data['accuracy']
        
        # Save model with metadata
        save_data = {
            'model': model_obj,
            'scaler': model_scaler,
            'label_encoder': label_encoder,
            'accuracy': acc,
            'model_type': model_name,
            'n_features': X.shape[1],
            'n_classes': len(label_encoder.classes_),
            'classes': label_encoder.classes_.tolist()
        }
        
        model_path = MODEL_DIR / f'{model_name}_model.pkl'
        joblib.dump(save_data, model_path)
        print(f"✓ Saved {model_name:.<20} ({acc:.4f})")
    
    # Save best model as default
    best_data = {
        'model': best_model,
        'scaler': best_scaler,
        'label_encoder': label_encoder,
        'accuracy': best_accuracy,
        'model_type': best_name,
        'n_features': X.shape[1],
        'n_classes': len(label_encoder.classes_),
        'classes': label_encoder.classes_.tolist()
    }
    
    default_path = MODEL_DIR / 'exercise_model.pkl'
    joblib.dump(best_data, default_path)
    print(f"\n✓ Best model ({best_name}) saved as: exercise_model.pkl")
    
    # Print summary
    print("\n" + "=" * 80)
    print("MODEL SUMMARY")
    print("=" * 80)
    for model_name in sorted(models_trained.keys()):
        acc = models_trained[model_name]['accuracy']
        print(f"{model_name:.<30} {acc:.4f} ({acc*100:.2f}%)")
    
    print("\n" + "=" * 80)
    print(f"BEST MODEL: {best_name.upper()}")
    print(f"Accuracy: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
    print("=" * 80)
    
    # Classification report for best model
    if best_name in ['svm', 'gradient_boosting']:
        y_pred = best_model.predict(X_test_scaled)
    else:
        y_pred = best_model.predict(X_test)
    
    print(f"\nDetailed Classification Report ({best_name.upper()}):")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
