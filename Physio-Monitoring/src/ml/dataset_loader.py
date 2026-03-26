import os
import sys
import numpy as np
import glob
import joblib

# Add project root to path to allow importing from models
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ml.dataset_config import UI_PMRD_PATH, KIMORE_PATH, UI_PMRD_MAPPING, KIMORE_MAPPING
# Import synthetic data generators
try:
    from models.exercise_recognition.create_shoulder_dataset import SHOULDER_EXERCISES, generate_synthetic_keypoints
except ImportError:
    # Fallback if import fails (e.g. run from different dir)
    print("Warning: Could not import synthetic generator directly. Using fallback.")
    SHOULDER_EXERCISES = {}

class DatasetLoader:
    """
    Unified loader for ML training data.
    Aggregates data from:
    1. Synthetic generation (Internal)
    2. UI-PMRD Dataset (External)
    3. KIMORE Dataset (External)
    """
    
    def __init__(self):
        self.features = []
        self.labels = []
        self.stats = {
            "synthetic": 0,
            "ui_pmrd": 0,
            "kimore": 0
        }

    def load_all(self):
        """Load data from all available sources"""
        print("Loading datasets...")
        
        # 1. Synthetic Data (Always available/generated)
        self._load_synthetic()
        
        # 2. UI-PMRD
        self._load_ui_pmrd()
        
        # 3. KIMORE
        self._load_kimore()
        
        print(f"Data loading complete. Total samples: {len(self.features)}")
        print(f"Breakdown: {self.stats}")
        
        return np.array(self.features), np.array(self.labels)

    def _load_synthetic(self):
        """Generate and load synthetic data frame-by-frame"""
        print("Generating synthetic data...")
        count = 0
        
        if not SHOULDER_EXERCISES:
            print("Error: Shoulder exercises configuration not found.")
            return

        for exercise_name, exercise_config in SHOULDER_EXERCISES.items():
            angles = exercise_config["angles"]
            repetitions = exercise_config["repetitions"]
            
            for rep in range(repetitions):
                angle_sequence = []
                # Check for plane in config, default to frontal if missing (replaces use_right_side logic too if we want)
                plane = exercise_config.get("plane", "frontal")
                
                for min_angle, max_angle, mid_angle in angles:
                    # 20 points per transition
                    # We generate a slightly wider range then cut off the ends to avoid "rest" poses
                    # which are identical across exercises (e.g. arm at side) and confuse the model
                    transition = np.linspace(min_angle, max_angle, 20)
                    
                    # Trim the first 4 and last 4 points of the transition sequence
                    # This removes the ambiguous start/end states
                    trimmed_transition = transition[4:-4]
                    
                    angle_sequence.extend(trimmed_transition)
                
                # Get raw keypoints for each frame (list of 132-float lists)
                # Pass plane to enable 3D coordinate generation
                keypoints_sequence = generate_synthetic_keypoints(angle_sequence, plane=plane)
                
                for frame_features in keypoints_sequence:
                    self.features.append(frame_features)
                    self.labels.append(exercise_name)
                    count += 1
        
        self.stats["synthetic"] = count
        print(f"  - Loaded {count} synthetic samples")

    def _load_ui_pmrd(self):
        """
        Load UI-PMRD dataset (Kinect Positions).
        Expected path: data/external/UI-PMRD/Segmented/Positions/*.txt
        Format: CSV with headers like 'Nose_X', 'Nose_Y', 'Nose_Z', etc. OR standard Kinect joint names.
        """
        if not os.path.exists(UI_PMRD_PATH):
            return

        print(f"Scanning UI-PMRD at {UI_PMRD_PATH}...")
        
        # Look for position files
        files = glob.glob(os.path.join(UI_PMRD_PATH, "**", "*positions*.txt"), recursive=True)
        files += glob.glob(os.path.join(UI_PMRD_PATH, "**", "*positions*.csv"), recursive=True)
        
        if not files:
            print("  - No position files found in UI-PMRD directory structure.")
            return

        count = 0
        import pandas as pd
        
        for fpath in files:
            try:
                # Infer label from filename (e.g., 'm01_s01' -> movement 01)
                # Map movement ID to label
                fname = os.path.basename(fpath)
                # Parse 'mXX' from filename
                parts = fname.split('_')
                if len(parts) < 1 or not parts[0].startswith('m'):
                    continue
                    
                move_id = parts[0] # e.g., "m01"
                label = UI_PMRD_MAPPING.get(move_id)
                
                if not label:
                    continue
                    
                # Load Data
                df = pd.read_csv(fpath, sep=',')
                
                # Check if comma separated or whitespace
                if df.shape[1] < 5:
                    df = pd.read_csv(fpath, sep='\s+')
                
                # Extract and map columns
                landmarks = self._map_to_mediapipe(df, "ui_pmrd")
                
                if landmarks is not None:
                    # landmarks shape: (n_frames, 33, 4) -> (n_frames, 132)
                    for frame in landmarks:
                        self.features.append(frame.flatten())
                        self.labels.append(label)
                        count += 1
                        
            except Exception as e:
                # print(f"Warning processing {fname}: {e}")
                continue

        self.stats["ui_pmrd"] = count
        print(f"  - Loaded {count} UI-PMRD samples")

    def _load_kimore(self):
        """
        Load KIMORE dataset.
        Expected path: data/external/KIMORE/Es1, Es2, etc. or GNE/CG folders.
        Format: CSV with 25 joints (X,Y,Z,State).
        """
        if not os.path.exists(KIMORE_PATH):
            return

        print(f"Scanning KIMORE at {KIMORE_PATH}...")
        
        # Look for files
        files = glob.glob(os.path.join(KIMORE_PATH, "**", "*.csv"), recursive=True)
        
        if not files:
            print("  - No CSV files found in KIMORE directory.")
            return

        count = 0
        import pandas as pd
        
        for fpath in files:
            try:
                # Infer label from parent folder or filename
                # KIMORE structure: .../Es1/Expert/.. or .../Es1/Subject/..
                # Es1 = Exercise 1
                path_parts = fpath.split(os.sep)
                
                # Find 'EsX' part
                ex_id = None
                for part in path_parts:
                    if part.startswith("Es") and part[2:].isdigit():
                        ex_id = part # e.g., "Es1"
                        break
                
                if not ex_id:
                     continue
                     
                label = KIMORE_MAPPING.get(ex_id)
                if not label:
                    continue

                # Load
                df = pd.read_csv(fpath)
                
                # Map
                landmarks = self._map_to_mediapipe(df, "kimore")
                
                if landmarks is not None:
                    for frame in landmarks:
                        self.features.append(frame.flatten())
                        self.labels.append(label)
                        count += 1
                        
            except Exception as e:
                continue

        self.stats["kimore"] = count
        print(f"  - Loaded {count} KIMORE samples")

    def _map_to_mediapipe(self, df, dataset_type):
        """
        Maps proprietary dataset columns to MediaPipe 33-landmark format (x, y, z, vis).
        Returns numpy array of shape (n_frames, 33, 4).
        """
        n_frames = len(df)
        outputs = np.zeros((n_frames, 33, 4)) # x,y,z,v
        
        # Column mapping helper
        # We need to find columns like "SpineBase_X" or similar.
        cols = df.columns
        
        # Map MP indices to potential column patterns (list of possible names)
        # MP Body: 11=L_Shoulder, 12=R_Shoulder, 13=L_Elbow, 14=R_Elbow, 15=L_Wrist, 16=R_Wrist
        # 23=L_Hip, 24=R_Hip, 25=L_Knee, 26=R_Knee, 27=L_Ankle, 28=R_Ankle
        
        base_mapping = {
            11: ["ShoulderLeft", "LeftShoulder", "LSHO"],
            12: ["ShoulderRight", "RightShoulder", "RSHO"],
            13: ["ElbowLeft", "LeftElbow", "LELB"],
            14: ["ElbowRight", "RightElbow", "RELB"],
            15: ["WristLeft", "LeftWrist", "LWRA"],
            16: ["WristRight", "RightWrist", "RWRA"],
            23: ["HipLeft", "LeftHip", "LeftHip", "L_Hip"], 
            24: ["HipRight", "RightHip", "RightHip", "R_Hip"],
            25: ["KneeLeft", "LeftKnee", "LKNE"],
            26: ["KneeRight", "RightKnee", "RKNE"],
            27: ["AnkleLeft", "LeftAnkle", "LANK"],
            28: ["AnkleRight", "RightAnkle", "RANK"]
        }
        
        # Normalize function 
        def get_xyz(row_idx, candidates):
            for base in candidates:
                # Try X, Y, Z suffixes
                try:
                    # Case 1: Header is "DeepSquat_SpineBase_X" or just "SpineBase_X"
                    # We look for a column strictly containing the base name and _X
                    matched_x = [c for c in cols if base in c and c.endswith('_X')]
                    matched_y = [c for c in cols if base in c and c.endswith('_Y')]
                    matched_z = [c for c in cols if base in c and c.endswith('_Z')]
                    
                    if matched_x and matched_y and matched_z:
                         x = df.iloc[row_idx][matched_x[0]]
                         y = df.iloc[row_idx][matched_y[0]]
                         z = df.iloc[row_idx][matched_z[0]]
                         return x, y, z
                except:
                    continue
            return 0, 0, 0

        try:
           for i in range(n_frames):
               # Fill key points
               for mp_idx, candidates in base_mapping.items():
                    x, y, z = get_xyz(i, candidates)
                    outputs[i, mp_idx] = [x, y, z, 1.0] # Visibility=1
               
           # Heuristic normalization: Check if units are mm (e.g. > 10) and convert to meters
           # Standard human height is ~1.7m. If we see values like 100 or 1000, it's likely mm or cm.
           max_val = np.max(np.abs(outputs[:, :, :3]))
           if max_val > 50: # Safe threshold (mm)
               print(f"    - Detected large coordinates (max={max_val:.1f}). Converting mm to meters.")
               outputs[:, :, :3] /= 1000.0
           elif max_val > 3: # Maybe cm? (e.g. 170cm)
               print(f"    - Detected large coordinates (max={max_val:.1f}). Converting cm to meters.")
               outputs[:, :, :3] /= 100.0
               
        except Exception:
            return None
            
        return outputs

if __name__ == "__main__":
    loader = DatasetLoader()
    X, y = loader.load_all()
    print(f"Shape: X={X.shape}, y={y.shape}")
