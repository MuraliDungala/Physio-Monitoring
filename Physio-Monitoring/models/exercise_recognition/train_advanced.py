"""
Advanced model training with hyperparameter tuning and algorithm comparison.
Trains multiple models (MLP, Random Forest, SVM) and selects the best.
"""

import pandas as pd
import numpy as np
import os
import joblib
import time
from pathlib import Path

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# Configuration
SCRIPT_DIR = Path(__file__).parent.parent.parent  # Go to Physio-Monitoring/
DATA_FILE = SCRIPT_DIR / "data/processed_keypoints/external_exercises.csv"
MODEL_DIR = SCRIPT_DIR / "models/exercise_recognition"
RESULTS_FILE = MODEL_DIR / "training_results.txt"

print("=" * 80)
print("ADVANCED MODEL TRAINING WITH HYPERPARAMETER TUNING")
print("=" * 80)

# Load data
print("\n[1/5] Loading data...")
start = time.time()
if not DATA_FILE.exists():
    raise FileNotFoundError(f"[ERROR] {DATA_FILE} not found")

df = pd.read_csv(str(DATA_FILE))
X = df.drop(columns=["exercise_label"]).values
y = df["exercise_label"].values

print(f"✓ Loaded {X.shape[0]} samples, {X.shape[1]} features")
print(f"  Exercises: {len(np.unique(y))}")
print(f"  Time: {time.time() - start:.2f}s")

# Encode labels
print("\n[2/5] Preprocessing...")
start = time.time()
label_encoder = LabelEncoder()
y_enc = label_encoder.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc,
    test_size=0.2,
    random_state=42,
    stratify=y_enc
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✓ Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
print(f"  Time: {time.time() - start:.2f}s")

# Store results
results = {}

# ============================================================================
# MODEL 1: MLP with Hyperparameter Tuning
# ============================================================================
print("\n[3/5] Training MLP with GridSearch...")
start = time.time()

mlp_params = {
    'hidden_layer_sizes': [(128, 64), (128, 64, 32)],
    'max_iter': [300, 500],
}

mlp_gs = GridSearchCV(
    MLPClassifier(random_state=42, early_stopping=True, validation_fraction=0.1),
    mlp_params,
    cv=2,
    scoring='accuracy',
    n_jobs=1,  # Single-threaded to avoid memory issues
    verbose=1
)

mlp_gs.fit(X_train_scaled, y_train)
mlp_best = mlp_gs.best_estimator_
mlp_acc = mlp_best.score(X_test_scaled, y_test)

print(f"✓ Best MLP params: {mlp_gs.best_params_}")
print(f"  Accuracy: {mlp_acc:.4f}")
print(f"  Time: {time.time() - start:.2f}s")

results['MLP'] = {
    'model': mlp_best,
    'accuracy': mlp_acc,
    'params': mlp_gs.best_params_
}

# ============================================================================
# MODEL 2: Random Forest with Hyperparameter Tuning
# ============================================================================
print("\n[3.5/5] Training Random Forest with GridSearch...")
start = time.time()

rf_params = {
    'n_estimators': [100, 200],
    'max_depth': [15, 20],
}

rf_gs = GridSearchCV(
    RandomForestClassifier(random_state=42, n_jobs=-1),
    rf_params,
    cv=2,
    scoring='accuracy',
    n_jobs=1,  # Single-threaded grid search to avoid memory issues
    verbose=1
)

rf_gs.fit(X_train, y_train)  # No scaling needed for RF
rf_best = rf_gs.best_estimator_
rf_acc = rf_best.score(X_test, y_test)

print(f"✓ Best RF params: {rf_gs.best_params_}")
print(f"  Accuracy: {rf_acc:.4f}")
print(f"  Time: {time.time() - start:.2f}s")

results['RandomForest'] = {
    'model': rf_best,
    'accuracy': rf_acc,
    'params': rf_gs.best_params_
}

# ============================================================================
# MODEL 3: SVM with Hyperparameter Tuning
# ============================================================================
print("\n[4/5] Training SVM with GridSearch...")
start = time.time()

svm_params = {
    'C': [10, 100],
    'kernel': ['rbf', 'poly'],
}

svm_gs = GridSearchCV(
    SVC(random_state=42, probability=True),
    svm_params,
    cv=2,
    scoring='accuracy',
    n_jobs=1,  # Single-threaded to avoid memory issues
    verbose=1
)

svm_gs.fit(X_train_scaled, y_train)
svm_best = svm_gs.best_estimator_
svm_acc = svm_best.score(X_test_scaled, y_test)

print(f"✓ Best SVM params: {svm_gs.best_params_}")
print(f"  Accuracy: {svm_acc:.4f}")
print(f"  Time: {time.time() - start:.2f}s")

results['SVM'] = {
    'model': svm_best,
    'accuracy': svm_acc,
    'params': svm_gs.best_params_
}

# ============================================================================
# Select Best Model
# ============================================================================
print("\n[5/5] Selecting best model...")
best_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
best_model = results[best_name]['model']
best_accuracy = results[best_name]['accuracy']

print("\n" + "=" * 80)
print("MODEL COMPARISON")
print("=" * 80)
for name, data in sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True):
    print(f"{name:.<30} {data['accuracy']:.4f}")

print("\n" + "=" * 80)
print(f"BEST MODEL: {best_name} ({best_accuracy:.4f})")
print("=" * 80)

# Detailed evaluation of best model
y_pred = best_model.predict(X_test_scaled if best_name in ['MLP', 'SVM'] else X_test)
print(f"\nDetailed Classification Report ({best_name}):")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

os.makedirs(MODEL_DIR, exist_ok=True)

# Save best model with full pipeline
if best_name == 'MLP':
    model_data = {
        'model': best_model,
        'scaler': scaler,
        'label_encoder': label_encoder,
        'model_type': 'MLP'
    }
elif best_name == 'RandomForest':
    model_data = {
        'model': best_model,
        'scaler': None,  # RF doesn't need scaling
        'label_encoder': label_encoder,
        'model_type': 'RandomForest'
    }
else:  # SVM
    model_data = {
        'model': best_model,
        'scaler': scaler,
        'label_encoder': label_encoder,
        'model_type': 'SVM'
    }

joblib.dump(model_data, str(MODEL_DIR / 'exercise_mlp.pkl'))

# Save detailed results
with open(str(RESULTS_FILE), 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("TRAINING RESULTS\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Best Model: {best_name}\n")
    f.write(f"Accuracy: {best_accuracy:.4f}\n")
    f.write(f"Parameters: {results[best_name]['params']}\n\n")
    f.write("Model Comparison:\n")
    for name, data in sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True):
        f.write(f"  {name}: {data['accuracy']:.4f}\n")

print(f"\n✅ Model saved to: {str(MODEL_DIR / 'exercise_mlp.pkl')}")
print(f"✅ Results saved to: {str(RESULTS_FILE)}")
