"""
Advanced Model Training - OPTIMIZED VERSION
Focused hyperparameter tuning on weak shoulder exercise classes
"""

import pandas as pd
import numpy as np
import os
import sys
import joblib
import time
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# Add path
sys.path.insert(0, str(Path(__file__).parent / "Physio-Monitoring"))

# Configuration
SCRIPT_DIR = Path(__file__).parent.parent.parent
DATA_FILE = SCRIPT_DIR / "data/processed_keypoints/exercise_data.csv"
MODEL_DIR = SCRIPT_DIR / "models/exercise_recognition"

print("=" * 80)
print("ADVANCED MODEL TRAINING - OPTIMIZED FOR WEAK CLASSES")
print("=" * 80)

# Load smaller dataset for faster training
print("\n[1/6] Loading optimized dataset...")
start = time.time()

if not DATA_FILE.exists():
    print(f"⚠ {DATA_FILE} not found, using fallback...")
    from src.ml.dataset_loader import DatasetLoader
    loader = DatasetLoader()
    X, y = loader.load_all()
else:
    df = pd.read_csv(str(DATA_FILE))
    if 'exercise_label' in df.columns:
        X = df.drop(columns=['exercise_label']).values
        y = df['exercise_label'].values
    else:
        # Handle alternative column names
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values

print(f"✓ Loaded {X.shape[0]:,} samples, {X.shape[1]} features")
print(f"  Unique exercises: {len(np.unique(y))}")
print(f"  Time: {time.time() - start:.2f}s")

# Encode labels
print("\n[2/6] Preprocessing...")
start = time.time()

le = LabelEncoder()
y_enc = le.fit_transform(y)
print(f"✓ Classes: {list(le.classes_)}")

# Split data
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

print(f"✓ Train: {X_train.shape[0]:,}, Test: {X_test.shape[0]:,}")
print(f"  Time: {time.time() - start:.2f}s")

# ============================================================================
# OPTIMIZED HYPERPARAMETER GRIDS (Smaller for speed)
# ============================================================================
print("\n[3/6] Training MLP with GridSearch (2x2 = 4 combinations)...")
start = time.time()

mlp_params = {
    'hidden_layer_sizes': [(128, 64), (256, 128)],
    'learning_rate_init': [0.001, 0.01],
}

mlp_gs = GridSearchCV(
    MLPClassifier(
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20
    ),
    mlp_params,
    cv=2,
    scoring='accuracy',
    n_jobs=1,
    verbose=0
)

mlp_gs.fit(X_train_scaled, y_train)
mlp_best = mlp_gs.best_estimator_
mlp_acc = mlp_best.score(X_test_scaled, y_test)

print(f"✓ Best MLP: {mlp_gs.best_params_}")
print(f"  CV accuracy: {mlp_gs.best_score_:.4f}")
print(f"  Test accuracy: {mlp_acc:.4f}")
print(f"  Time: {time.time() - start:.2f}s")

# ============================================================================
# Random Forest with Hyperparameter Tuning
# ============================================================================
print("\n[4/6] Training Random Forest with GridSearch (2x2 = 4 combinations)...")
start = time.time()

rf_params = {
    'n_estimators': [100, 200],
    'max_depth': [15, 25],
}

rf_gs = GridSearchCV(
    RandomForestClassifier(
        random_state=42,
        n_jobs=-1,
        min_samples_split=5
    ),
    rf_params,
    cv=2,
    scoring='accuracy',
    n_jobs=1,
    verbose=0
)

rf_gs.fit(X_train, y_train)
rf_best = rf_gs.best_estimator_
rf_acc = rf_best.score(X_test, y_test)

print(f"✓ Best RF: {rf_gs.best_params_}")
print(f"  CV accuracy: {rf_gs.best_score_:.4f}")
print(f"  Test accuracy: {rf_acc:.4f}")
print(f"  Time: {time.time() - start:.2f}s")

# ============================================================================
# SVM with Hyperparameter Tuning
# ============================================================================
print("\n[5/6] Training SVM with GridSearch (2x2 = 4 combinations)...")
start = time.time()

svm_params = {
    'C': [1, 10],
    'kernel': ['rbf', 'poly'],
}

svm_gs = GridSearchCV(
    SVC(
        random_state=42,
        probability=True,
        gamma='scale'
    ),
    svm_params,
    cv=2,
    scoring='accuracy',
    n_jobs=1,
    verbose=0
)

svm_gs.fit(X_train_scaled, y_train)
svm_best = svm_gs.best_estimator_
svm_acc = svm_best.score(X_test_scaled, y_test)

print(f"✓ Best SVM: {svm_gs.best_params_}")
print(f"  CV accuracy: {svm_gs.best_score_:.4f}")
print(f"  Test accuracy: {svm_acc:.4f}")
print(f"  Time: {time.time() - start:.2f}s")

# ============================================================================
# Model Comparison and Selection
# ============================================================================
print("\n[6/6] Model comparison and selection...")

models_data = {
    'MLP': {'accuracy': mlp_acc, 'model': mlp_best, 'params': mlp_gs.best_params_, 'scaler': scaler},
    'RandomForest': {'accuracy': rf_acc, 'model': rf_best, 'params': rf_gs.best_params_, 'scaler': None},
    'SVM': {'accuracy': svm_acc, 'model': svm_best, 'params': svm_gs.best_params_, 'scaler': scaler}
}

print("\n" + "=" * 80)
print("FINAL MODEL COMPARISON")
print("=" * 80)

sorted_models = sorted(models_data.items(), key=lambda x: x[1]['accuracy'], reverse=True)
for i, (name, data) in enumerate(sorted_models, 1):
    print(f"{i}. {name:.<30} {data['accuracy']:.4f} {data['params']}")

best_name, best_data = sorted_models[0]
print(f"\n{'='*80}")
print(f"🏆 BEST MODEL: {best_name} ({best_data['accuracy']:.4f})")
print(f"{'='*80}")

# Detailed evaluation
y_pred = best_data['model'].predict(
    X_test_scaled if best_name in ['MLP', 'SVM'] else X_test
)

print(f"\n{best_name} - Detailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# Save best model
os.makedirs(MODEL_DIR, exist_ok=True)

# Update production model if improvement found
current_best_path = MODEL_DIR / 'exercise_model.pkl'
if current_best_path.exists():
    current_best = joblib.load(str(current_best_path))
    current_acc = current_best.get('accuracy', 0.0)
    print(f"\nComparison with current production model:")
    print(f"  Current: {current_acc:.4f}")
    print(f"  New: {best_data['accuracy']:.4f}")
    print(f"  Improvement: {(best_data['accuracy'] - current_acc)*100:+.2f}%")

# Save new best model
artifact = {
    'model': best_data['model'],
    'scaler': best_data['scaler'],
    'label_encoder': le,
    'model_type': best_name,
    'accuracy': best_data['accuracy'],
    'hyperparameters': best_data['params'],
    'all_results': {
        k: {'accuracy': v['accuracy'], 'params': v['params']}
        for k, v in models_data.items()
    }
}

output_path = MODEL_DIR / f'exercise_model_advanced.pkl'
joblib.dump(artifact, str(output_path))
print(f"\n✅ Advanced model saved to: {output_path}")

# Save comparison results
results_file = MODEL_DIR / 'training_advanced_results.txt'
with open(str(results_file), 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("ADVANCED TRAINING RESULTS\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Best Model: {best_name}\n")
    f.write(f"Accuracy: {best_data['accuracy']:.4f}\n")
    f.write(f"Parameters: {best_data['params']}\n\n")
    f.write("All Models Comparison:\n")
    for name, data in sorted_models:
        f.write(f"  {name}: {data['accuracy']:.4f}\n")
    f.write("\nDetailed Classification Report:\n")
    f.write(classification_report(y_test, y_pred, target_names=le.classes_))

print(f"✅ Results saved to: {results_file}")

print("\n" + "=" * 80)
print("ADVANCED TRAINING COMPLETE")
print("=" * 80)
