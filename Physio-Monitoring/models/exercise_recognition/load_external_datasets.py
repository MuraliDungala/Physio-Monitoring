"""
Load and process KIMORE and UI-PMRD external datasets with appropriate labeling.
- KIMORE: Numerical joint angle labels (for regression/form quality)
- UI-PMRD: Binary correct/incorrect labels (for form classification)
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

# Dataset paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXTERNAL_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "external")
UI_PMRD_PATH = os.path.join(EXTERNAL_DATA_DIR, "UI-PMRD")
KIMORE_PATH = os.path.join(EXTERNAL_DATA_DIR, "KIMORE")

# Exercise mapping from external datasets to internal names
UI_PMRD_EXERCISE_MAPPING = {
    "UI_PRMD_ex1": "Shoulder Flexion",
    "UI_PRMD_ex2": "Shoulder Abduction", 
    "UI_PRMD_ex3": "Shoulder Extension",
    "UI_PRMD_ex4": "Shoulder Internal Rotation",
    "UI_PRMD_ex5": "Shoulder External Rotation",
    "UI_PRMD_ex6": "Elbow Flexion",
    "UI_PRMD_ex7": "Elbow Extension",
    "UI_PRMD_ex8": "Hip Abduction",
    "UI_PRMD_ex9": "Knee Flexion",
    "UI_PRMD_ex10": "Trunk Rotation",
}

KIMORE_EXERCISE_MAPPING = {
    "Kimore ex1": "Shoulder Flexion",
    "Kimore ex2": "Lateral Trunk Tilt",
    "Kimore ex3": "Trunk Rotation",
    "Kimore ex4": "Pelvis Rotation",
    "Kimore ex5": "Knee Flexion",
}


def load_kimore_data():
    """
    Load KIMORE dataset: Train_X.csv (features) + Train_Y.csv (labels)
    Note: KIMORE has 100 frames per repetition, Y has one label per rep
    Returns: DataFrame with features and exercise/angle labels
    """
    all_data = []
    
    for exercise_folder in os.listdir(KIMORE_PATH):
        if not exercise_folder.startswith("Kimore"):
            continue
            
        folder_path = os.path.join(KIMORE_PATH, exercise_folder)
        if not os.path.isdir(folder_path):
            continue
            
        train_x_path = os.path.join(folder_path, "Train_X.csv")
        train_y_path = os.path.join(folder_path, "Train_Y.csv")
        
        if not os.path.exists(train_x_path) or not os.path.exists(train_y_path):
            print(f"⚠️ Missing files in {exercise_folder}")
            continue
        
        try:
            X = pd.read_csv(train_x_path, header=None)
            Y = pd.read_csv(train_y_path, header=None).values.flatten()
            
            # KIMORE structure: 100 frames per repetition
            frames_per_rep = 100
            n_reps = len(Y)
            
            # Repeat labels for each frame in the repetition
            repeated_labels = np.repeat(Y, frames_per_rep)
            
            # Verify dimensions match
            if len(repeated_labels) != len(X):
                print(f"⚠️ Shape mismatch in {exercise_folder}: X={len(X)}, Y*{frames_per_rep}={len(repeated_labels)}")
                # Try to handle by truncating to smaller size
                min_len = min(len(repeated_labels), len(X))
                X = X.iloc[:min_len]
                repeated_labels = repeated_labels[:min_len]
            
            # Reset index before adding columns
            X = X.reset_index(drop=True)
            
            # Add labels
            exercise_name = KIMORE_EXERCISE_MAPPING.get(exercise_folder, exercise_folder)
            X["exercise"] = exercise_name
            X["form_quality"] = pd.Series(repeated_labels, index=X.index)
            X["source"] = "KIMORE"
            
            all_data.append(X)
            print(f"✓ Loaded {exercise_folder}: {X.shape[0]} samples ({n_reps} reps)")
            
        except Exception as e:
            print(f"✗ Error loading {exercise_folder}: {e}")
    
    if not all_data:
        print("⚠️ No KIMORE data loaded")
        return None
    
    return pd.concat(all_data, ignore_index=True)


def load_ui_pmrd_data():
    """
    Load UI-PMRD dataset: Data_Correct.csv + Data_Incorrect.csv
    Returns: DataFrame with binary form correctness label
    """
    all_data = []
    
    for exercise_folder in sorted(os.listdir(UI_PMRD_PATH)):
        if not exercise_folder.startswith("UI_PRMD"):
            continue
            
        folder_path = os.path.join(UI_PMRD_PATH, exercise_folder)
        if not os.path.isdir(folder_path):
            continue
        
        exercise_name = UI_PMRD_EXERCISE_MAPPING.get(exercise_folder, exercise_folder)
        
        # Load correct form data
        correct_path = os.path.join(folder_path, "Data_Correct.csv")
        if os.path.exists(correct_path):
            try:
                df_correct = pd.read_csv(correct_path, header=None)
                df_correct["exercise"] = exercise_name
                df_correct["form_correct"] = 1  # Binary label: 1 = correct
                df_correct["source"] = "UI-PMRD-Correct"
                all_data.append(df_correct)
                print(f"✓ Loaded {exercise_folder} (Correct): {df_correct.shape[0]} samples")
            except Exception as e:
                print(f"✗ Error loading {exercise_folder} correct data: {e}")
        
        # Load incorrect form data
        incorrect_path = os.path.join(folder_path, "Data_Incorrect.csv")
        if os.path.exists(incorrect_path):
            try:
                df_incorrect = pd.read_csv(incorrect_path, header=None)
                df_incorrect["exercise"] = exercise_name
                df_incorrect["form_correct"] = 0  # Binary label: 0 = incorrect
                df_incorrect["source"] = "UI-PMRD-Incorrect"
                all_data.append(df_incorrect)
                print(f"✓ Loaded {exercise_folder} (Incorrect): {df_incorrect.shape[0]} samples")
            except Exception as e:
                print(f"✗ Error loading {exercise_folder} incorrect data: {e}")
    
    if not all_data:
        print("⚠️ No UI-PMRD data loaded")
        return None
    
    return pd.concat(all_data, ignore_index=True)


def combine_datasets():
    """
    Load and combine KIMORE and UI-PMRD datasets.
    KIMORE: For regression (numerical form quality scores)
    UI-PMRD: For classification (binary correct/incorrect)
    """
    print("\n" + "="*60)
    print("LOADING EXTERNAL DATASETS")
    print("="*60 + "\n")
    
    # Load KIMORE (regression task)
    print("Loading KIMORE Dataset (Form Quality Regression):")
    print("-" * 50)
    kimore_df = load_kimore_data()
    
    print("\nLoading UI-PMRD Dataset (Form Classification):")
    print("-" * 50)
    ui_pmrd_df = load_ui_pmrd_data()
    
    print("\n" + "="*60)
    
    # Summary statistics
    if kimore_df is not None:
        print(f"\n✓ KIMORE Summary:")
        print(f"  - Total samples: {kimore_df.shape[0]}")
        print(f"  - Exercises: {kimore_df['exercise'].nunique()}")
        print(f"  - Features: {kimore_df.shape[1] - 3}")  # Exclude label columns
        print(f"  - Form Quality Range: {kimore_df['form_quality'].min():.2f} - {kimore_df['form_quality'].max():.2f}")
    
    if ui_pmrd_df is not None:
        print(f"\n✓ UI-PMRD Summary:")
        print(f"  - Total samples: {ui_pmrd_df.shape[0]}")
        print(f"  - Exercises: {ui_pmrd_df['exercise'].nunique()}")
        print(f"  - Features: {ui_pmrd_df.shape[1] - 3}")  # Exclude label columns
        print(f"  - Correct: {(ui_pmrd_df['form_correct'] == 1).sum()}")
        print(f"  - Incorrect: {(ui_pmrd_df['form_correct'] == 0).sum()}")
    
    return kimore_df, ui_pmrd_df


def save_combined_dataset(kimore_df, ui_pmrd_df, output_dir="data/processed_keypoints"):
    """
    Save combined datasets separately for different ML tasks
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save KIMORE for regression task
    if kimore_df is not None:
        output_path = os.path.join(output_dir, "external_kimore_regression.csv")
        try:
            kimore_df.to_csv(output_path, index=False)
            print(f"\n✓ Saved KIMORE dataset: {output_path}")
        except Exception as e:
            print(f"\n✗ Failed to save KIMORE: {e}")
    
    # Save UI-PMRD for classification task
    if ui_pmrd_df is not None:
        output_path = os.path.join(output_dir, "external_ui_pmrd_classification.csv")
        try:
            ui_pmrd_df.to_csv(output_path, index=False)
            print(f"✓ Saved UI-PMRD dataset: {output_path}")
        except Exception as e:
            print(f"✗ Failed to save UI-PMRD: {e}")


if __name__ == "__main__":
    kimore_df, ui_pmrd_df = combine_datasets()
    
    output_dir = os.path.join(PROJECT_ROOT, "data", "processed_keypoints")
    save_combined_dataset(kimore_df, ui_pmrd_df, output_dir)
    
    print("\n" + "="*60)
    print("✓ DATASET LOADING COMPLETE")
    print("="*60)
    print("\nUse these datasets for:")
    print("  1. external_kimore_regression.csv → Train form quality models")
    print("  2. external_ui_pmrd_classification.csv → Train form correctness classifier")
    print("  3. external_combined.csv → General multi-task learning")
