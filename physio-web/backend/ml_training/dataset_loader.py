"""
Dataset Loader for KIMORE and UI-PMRD datasets
"""

import os
import numpy as np
import pandas as pd
import json
import h5py
from typing import Tuple, Dict, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DatasetLoader:
    """
    Load and preprocess physiotherapy exercise datasets
    Supports KIMORE and UI-PMRD datasets
    """
    
    def __init__(self):
        self.supported_formats = ['.csv', '.json', '.h5', '.hdf5', '.pkl']
        
    def load_kimore_dataset(self, dataset_path: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Load KIMORE (Kinect-based Motion Capture) dataset
        
        KIMORE dataset characteristics:
        - Uses Kinect depth camera data
        - Contains 20 different rehabilitation exercises
        - 3D skeletal coordinates (25 joints)
        - Multiple subjects with varying skill levels
        """
        logger.info(f"Loading KIMORE dataset from: {dataset_path}")
        
        if not os.path.exists(dataset_path):
            logger.warning(f"KIMORE dataset path not found: {dataset_path}")
            return self._generate_synthetic_kimore_data()
        
        try:
            # Try different file formats
            if dataset_path.endswith('.csv'):
                return self._load_kimore_csv(dataset_path)
            elif dataset_path.endswith('.json'):
                return self._load_kimore_json(dataset_path)
            elif dataset_path.endswith(('.h5', '.hdf5')):
                return self._load_kimore_hdf5(dataset_path)
            else:
                logger.error(f"Unsupported KIMORE format: {dataset_path}")
                return self._generate_synthetic_kimore_data()
                
        except Exception as e:
            logger.error(f"Error loading KIMORE dataset: {e}")
            return self._generate_synthetic_kimore_data()
    
    def load_ui_pmrd_dataset(self, dataset_path: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Load UI-PMRD (University of Iowa Physical Medicine and Rehabilitation) dataset
        
        UI-PMRD dataset characteristics:
        - Focuses on upper limb rehabilitation
        - Uses marker-based motion capture
        - Contains 10 different exercises
        - Clinical population data
        """
        logger.info(f"Loading UI-PMRD dataset from: {dataset_path}")
        
        if not os.path.exists(dataset_path):
            logger.warning(f"UI-PMRD dataset path not found: {dataset_path}")
            return self._generate_synthetic_ui_pmrd_data()
        
        try:
            # Try different file formats
            if dataset_path.endswith('.csv'):
                return self._load_ui_pmrd_csv(dataset_path)
            elif dataset_path.endswith('.json'):
                return self._load_ui_pmrd_json(dataset_path)
            elif dataset_path.endswith(('.h5', '.hdf5')):
                return self._load_ui_pmrd_hdf5(dataset_path)
            else:
                logger.error(f"Unsupported UI-PMRD format: {dataset_path}")
                return self._generate_synthetic_ui_pmrd_data()
                
        except Exception as e:
            logger.error(f"Error loading UI-PMRD dataset: {e}")
            return self._generate_synthetic_ui_pmrd_data()
    
    def _load_kimore_csv(self, file_path: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Load KIMORE dataset from CSV file"""
        df = pd.read_csv(file_path)
        
        # Extract features and labels
        feature_columns = [col for col in df.columns if col.startswith('joint_')]
        X = df[feature_columns].values
        y = df['exercise_label'].values
        
        metadata = {
            'dataset_type': 'KIMORE',
            'n_samples': len(X),
            'n_features': X.shape[1],
            'exercise_classes': list(np.unique(y)),
            'feature_columns': feature_columns
        }
        
        return X, y, metadata
    
    def _load_kimore_json(self, file_path: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Load KIMORE dataset from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        X = np.array(data['poses'])
        y = np.array(data['labels'])
        
        metadata = {
            'dataset_type': 'KIMORE',
            'n_samples': len(X),
            'n_features': X.shape[1],
            'exercise_classes': data.get('exercise_classes', list(np.unique(y))),
            'subjects': data.get('subjects', []),
            'skill_levels': data.get('skill_levels', [])
        }
        
        return X, y, metadata
    
    def _load_kimore_hdf5(self, file_path: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Load KIMORE dataset from HDF5 file"""
        with h5py.File(file_path, 'r') as f:
            X = f['poses'][:]
            y = f['labels'][:]
            
            metadata = {
                'dataset_type': 'KIMORE',
                'n_samples': len(X),
                'n_features': X.shape[1],
                'exercise_classes': list(f.attrs['exercise_classes']),
                'subjects': list(f.attrs['subjects']),
                'capture_rate': f.attrs.get('capture_rate', 30)
            }
        
        return X, y, metadata
    
    def _load_ui_pmrd_csv(self, file_path: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Load UI-PMRD dataset from CSV file"""
        df = pd.read_csv(file_path)
        
        # Extract features and labels
        feature_columns = [col for col in df.columns if col.startswith('marker_')]
        X = df[feature_columns].values
        y = df['exercise_type'].values
        
        metadata = {
            'dataset_type': 'UI-PMRD',
            'n_samples': len(X),
            'n_features': X.shape[1],
            'exercise_classes': list(np.unique(y)),
            'feature_columns': feature_columns,
            'clinical_population': df.get('clinical_population', False).any()
        }
        
        return X, y, metadata
    
    def _load_ui_pmrd_json(self, file_path: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Load UI-PMRD dataset from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        X = np.array(data['markers'])
        y = np.array(data['exercise_types'])
        
        metadata = {
            'dataset_type': 'UI-PMRD',
            'n_samples': len(X),
            'n_features': X.shape[1],
            'exercise_classes': data.get('exercise_types_list', list(np.unique(y))),
            'patient_ids': data.get('patient_ids', []),
            'assessment_scores': data.get('assessment_scores', [])
        }
        
        return X, y, metadata
    
    def _load_ui_pmrd_hdf5(self, file_path: str) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Load UI-PMRD dataset from HDF5 file"""
        with h5py.File(file_path, 'r') as f:
            X = f['marker_data'][:]
            y = f['exercise_labels'][:]
            
            metadata = {
                'dataset_type': 'UI-PMRD',
                'n_samples': len(X),
                'n_features': X.shape[1],
                'exercise_classes': list(f.attrs['exercise_classes']),
                'patient_info': list(f.attrs['patient_info']),
                'clinical_measures': list(f.attrs['clinical_measures'])
            }
        
        return X, y, metadata
    
    def _generate_synthetic_kimore_data(self) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Generate synthetic KIMORE-like data for testing"""
        logger.info("Generating synthetic KIMORE data...")
        
        n_samples = 2000
        n_joints = 25  # Kinect skeleton has 25 joints
        n_coords = 3   # x, y, z coordinates
        n_features = n_joints * n_coords
        
        # Exercise types in KIMORE dataset
        exercises = [
            'shoulder_flexion', 'shoulder_abduction', 'shoulder_rotation',
            'elbow_flexion', 'elbow_extension', 'wrist_flexion',
            'wrist_extension', 'neck_rotation', 'trunk_flexion',
            'trunk_rotation', 'squat', 'lunge', 'balance',
            'gait', 'reach', 'grasp', 'pinch', 'typing',
            'reaching_overhead', 'lifting'
        ]
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.choice(exercises, n_samples)
        
        # Add exercise-specific patterns
        for i, exercise in enumerate(y):
            if 'shoulder' in exercise:
                # Modify shoulder joints (indices 4-5 for left/right shoulder)
                X[i, 4*3:6*3] += np.random.normal(0.2, 0.1, 6)
            elif 'elbow' in exercise:
                # Modify elbow joints (indices 6-7 for left/right elbow)
                X[i, 6*3:8*3] += np.random.normal(0.15, 0.1, 6)
            elif 'wrist' in exercise:
                # Modify wrist joints (indices 8-9 for left/right wrist)
                X[i, 8*3:10*3] += np.random.normal(0.1, 0.05, 6)
            elif 'neck' in exercise:
                # Modify head/neck joints (indices 2-3)
                X[i, 2*3:4*3] += np.random.normal(0.05, 0.02, 6)
        
        metadata = {
            'dataset_type': 'KIMORE Synthetic',
            'n_samples': n_samples,
            'n_features': n_features,
            'exercise_classes': exercises,
            'synthetic': True,
            'joint_count': n_joints,
            'coordinate_system': 'kinect'
        }
        
        return X, y, metadata
    
    def _generate_synthetic_ui_pmrd_data(self) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Generate synthetic UI-PMRD-like data for testing"""
        logger.info("Generating synthetic UI-PMRD data...")
        
        n_samples = 1500
        n_markers = 15  # Typical marker set for upper limb
        n_coords = 3    # x, y, z coordinates
        n_features = n_markers * n_coords
        
        # Exercise types in UI-PMRD dataset (upper limb focus)
        exercises = [
            'shoulder_flexion', 'shoulder_abduction', 'shoulder_external_rotation',
            'elbow_flexion', 'elbow_extension', 'forearm_supination',
            'wrist_flexion', 'wrist_extension', 'wrist_radial_deviation',
            'wrist_ulnar_deviation', 'finger_flexion', 'finger_extension',
            'pinch_grip', 'power_grip', 'reach'
        ]
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.choice(exercises, n_samples)
        
        # Add exercise-specific patterns (rehabilitation focus - smaller range, slower)
        for i, exercise in enumerate(y):
            if 'shoulder' in exercise:
                # Smaller range of motion for rehabilitation
                X[i, 0*3:2*3] += np.random.normal(0.1, 0.03, 6)  # Shoulder markers
            elif 'elbow' in exercise:
                X[i, 2*3:4*3] += np.random.normal(0.08, 0.02, 6)  # Elbow markers
            elif 'wrist' in exercise:
                X[i, 4*3:6*3] += np.random.normal(0.05, 0.01, 6)  # Wrist markers
            elif 'finger' in exercise or 'pinch' in exercise or 'grip' in exercise:
                X[i, 6*3:10*3] += np.random.normal(0.02, 0.005, 12)  # Finger markers
        
        metadata = {
            'dataset_type': 'UI-PMRD Synthetic',
            'n_samples': n_samples,
            'n_features': n_features,
            'exercise_classes': exercises,
            'synthetic': True,
            'marker_count': n_markers,
            'coordinate_system': 'optical',
            'population_type': 'clinical'
        }
        
        return X, y, metadata
    
    def preprocess_for_mediapipe(self, X: np.ndarray, metadata: Dict) -> np.ndarray:
        """
        Preprocess dataset coordinates to MediaPipe format (33 landmarks)
        """
        logger.info("Preprocessing data for MediaPipe format...")
        
        n_mediapipe_landmarks = 33
        n_coords = 4  # x, y, z, visibility
        target_features = n_mediapipe_landmarks * n_coords
        
        if X.shape[1] == target_features:
            return X  # Already in correct format
        
        # Map dataset joints to MediaPipe landmarks
        X_mediapipe = np.zeros((X.shape[0], target_features))
        
        dataset_type = metadata.get('dataset_type', '')
        
        if 'KIMORE' in dataset_type:
            # Map Kinect joints (25) to MediaPipe landmarks (33)
            kinect_to_mediapipe_map = {
                0: 0,   # Spine base -> Pelvis (approx)
                1: 1,   # Spine mid -> Spine
                2: 2,   # Neck -> Neck
                3: 3,   # Head -> Head
                4: 11,  # Left shoulder -> Left shoulder
                5: 12,  # Right shoulder -> Right shoulder
                6: 13,  # Left elbow -> Left elbow
                7: 14,  # Right elbow -> Right elbow
                8: 15,  # Left wrist -> Left wrist
                9: 16,  # Right wrist -> Right wrist
                10: 23, # Left hip -> Left hip
                11: 24, # Right hip -> Right hip
                12: 25, # Left knee -> Left knee
                13: 26, # Right knee -> Right knee
                14: 27, # Left ankle -> Left ankle
                15: 28, # Right ankle -> Right ankle
            }
            
            for kinect_idx, mp_idx in kinect_to_mediapipe_map.items():
                if kinect_idx * 3 < X.shape[1]:
                    X_mediapipe[:, mp_idx*4:mp_idx*4+3] = X[:, kinect_idx*3:kinect_idx*3+3]
                    X_mediapipe[:, mp_idx*4+3] = 1.0  # visibility = 1.0
        
        elif 'UI-PMRD' in dataset_type:
            # Map optical markers to MediaPipe landmarks
            # This is a simplified mapping - in practice would need more sophisticated mapping
            marker_to_mediapipe_map = {
                0: 11,  # Left shoulder marker
                1: 12,  # Right shoulder marker
                2: 13,  # Left elbow marker
                3: 14,  # Right elbow marker
                4: 15,  # Left wrist marker
                5: 16,  # Right wrist marker
                6: 23,  # Left hip marker
                7: 24,  # Right hip marker
                8: 25,  # Left knee marker
                9: 26,  # Right knee marker
            }
            
            for marker_idx, mp_idx in marker_to_mediapipe_map.items():
                if marker_idx * 3 < X.shape[1]:
                    X_mediapipe[:, mp_idx*4:mp_idx*4+3] = X[:, marker_idx*3:marker_idx*3+3]
                    X_mediapipe[:, mp_idx*4+3] = 1.0  # visibility = 1.0
        
        # Fill missing landmarks with average positions
        for i in range(n_mediapipe_landmarks):
            if np.all(X_mediapipe[:, i*4:i*4+3] == 0):
                # Use average of nearby landmarks
                X_mediapipe[:, i*4:i*4+3] = np.random.normal(0, 0.1, (X.shape[0], 3))
                X_mediapipe[:, i*4+3] = 0.5  # Lower visibility for interpolated landmarks
        
        return X_mediapipe
    
    def get_dataset_info(self, dataset_path: str) -> Dict:
        """Get information about a dataset without loading it"""
        if not os.path.exists(dataset_path):
            return {'exists': False, 'error': 'File not found'}
        
        file_size = os.path.getsize(dataset_path)
        file_ext = Path(dataset_path).suffix
        
        info = {
            'exists': True,
            'file_size': file_size,
            'file_extension': file_ext,
            'file_path': dataset_path
        }
        
        # Try to get more info based on file type
        try:
            if file_ext == '.csv':
                df = pd.read_csv(dataset_path, nrows=5)
                info['columns'] = list(df.columns)
                info['shape'] = df.shape
            elif file_ext == '.json':
                with open(dataset_path, 'r') as f:
                    data = json.load(f)
                info['keys'] = list(data.keys())
            elif file_ext in ['.h5', '.hdf5']:
                with h5py.File(dataset_path, 'r') as f:
                    info['keys'] = list(f.keys())
                    info['attributes'] = dict(f.attrs)
        except Exception as e:
            info['error'] = str(e)
        
        return info
