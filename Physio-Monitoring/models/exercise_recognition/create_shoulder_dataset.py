"""
Training data generator for shoulder exercises.
Creates synthetic training data for ML model to recognize all shoulder movements.
"""

import os
import csv
import numpy as np
from pathlib import Path

# Shoulder exercise definitions with representative angle ranges
SHOULDER_EXERCISES = {
    "Shoulder Flexion": {
        "angles": [
            (20, 150, 80),
            (150, 20, 80),
        ],
        "repetitions": 5,
        "plane": "sagittal"
    },
    "Shoulder Extension": {
        "angles": [
            (0, 50, 25),
            (50, 0, 25),
        ],
        "repetitions": 5,
        "plane": "sagittal_neg"
    },
    "Shoulder Abduction": {
        "angles": [
            (20, 160, 90),
            (160, 20, 90),
        ],
        "repetitions": 5,
        "plane": "frontal"
    },
    "Shoulder Adduction": {
        "angles": [
            (160, 20, 90),
            (20, 160, 90),
        ],
        "repetitions": 5,
        "plane": "frontal"
    },
    "Shoulder Internal Rotation": {
        "angles": [
            (5, 80, 45),
            (80, 5, 45),
        ],
        "repetitions": 5,
        "plane": "transverse_rot"
    },
    "Shoulder External Rotation": {
        "angles": [
            (5, 80, 45),
            (80, 5, 45),
        ],
        "repetitions": 5,
        "plane": "transverse_rot_neg"
    },
    "Shoulder Horizontal Abduction": {
        "angles": [
            (20, 100, 60),
            (100, 20, 60),
        ],
        "repetitions": 5,
        "plane": "transverse"
    },
    "Shoulder Horizontal Adduction": {
        "angles": [
            (120, 20, 70),
            (20, 120, 70),
        ],
        "repetitions": 5,
        "plane": "transverse_cross"
    },
    "Shoulder Circumduction": {
        "angles": [
            (90, 270, 180),
            (270, 90, 180),
        ],
        "repetitions": 3,
        "plane": "frontal"  # Simplified
    },
    "Elbow Flexion": {
        "angles": [
            (70, 140, 100),
            (140, 70, 100),
        ],
        "repetitions": 5,
        "plane": "sagittal_arm"
    },
    "Knee Flexion": {
        "angles": [
            (90, 165, 130),
            (165, 90, 130),
        ],
        "repetitions": 5,
        "plane": "sagittal_leg"
    },
    "Hip Abduction": {
        "angles": [
            (30, 110, 70),
            (110, 30, 70),
        ],
        "repetitions": 5,
        "plane": "frontal_leg"
    },
}

# Landmark indices for MediaPipe pose
SHOULDER_L = 11
SHOULDER_R = 12
ELBOW_L = 13
ELBOW_R = 14
WRIST_L = 15
WRIST_R = 16
HIP_L = 23
HIP_R = 24
KNEE_L = 25
KNEE_R = 26
ANKLE_L = 27
ANKLE_R = 28

NUM_LANDMARKS = 33

def generate_synthetic_keypoints(angle_sequence, use_right_side=True, plane="frontal"):
    """
    Generate synthetic keypoints for a sequence of angles.
    
    Args:
        angle_sequence: List of angles to follow
        use_right_side: Use right side landmarks (True) or left side (False)
        plane: Movement plane (frontal, sagittal, transverse, etc.)
        
    Returns:
        List of keypoint arrays (each array = one frame)
    """
    keypoints_list = []
    frames_per_angle = 10  # 10 frames per angle transition
    
    for i, angle in enumerate(angle_sequence):
        # Interpolate between current and next angle
        current_angle = angle
        
        # Keep static for this angle step (mimicking discrete steps or smoothed later)
        angle_progress = np.linspace(0, 1, frames_per_angle)
        
        for progress in angle_progress:
            # Create base keypoint array (all zeros)
            keypoints = [0.0] * (NUM_LANDMARKS * 4)
            
            # Generate keypoints based on angle
            # Use right side landmarks
            shoulder_idx = SHOULDER_R
            elbow_idx = ELBOW_R
            wrist_idx = WRIST_R
            hip_idx = HIP_R
            knee_idx = KNEE_R
            ankle_idx = ANKLE_R
            
            # Generate position data (x, y, z, visibility)
            # These are normalized coordinates (0-1)
            
            # Shoulder at center
            shoulder_x, shoulder_y, shoulder_z = 0.5, 0.4, 0.0
            
            # 3D Math based on plane
            angle_rad = np.radians(current_angle)
            arm_len = 0.15
            forearm_len = 0.12
            
            # Defaults
            elbow_x, elbow_y, elbow_z = shoulder_x, shoulder_y + arm_len, 0.0
            wrist_x, wrist_y, wrist_z = elbow_x, elbow_y + forearm_len, 0.0
            
            # === UPPER BODY PLANES ===
            
            if plane == "frontal":
                # Abduction: Moving in XY plane (Z=0)
                # 0 deg = down (0, 1), 90 deg = side (1, 0), 180 deg = up (0, -1)
                # Our angles: 20 (side-down) to 160 (side-up)
                # Correct math for shoulder angle relative to vertical down
                # cos(theta) for y, sin(theta) for x? 
                # Angle 0 is down. Angle 90 is side.
                # x = sin(angle), y = cos(angle) (downwards positive)
                # Actually, standard unit circle: 0 is right. -90 is up. 90 is down.
                # Let's approximate: 20 deg from body. 
                eff_angle = np.radians(current_angle + 90) # 0->90 (down), 90->180 (side)? No.
                # Simple Manual Projection
                # 0 deg = (0, 1) relative to shoulder. 
                # 90 deg = (1, 0) relative to shoulder.
                elbow_x = shoulder_x + arm_len * np.sin(angle_rad)
                elbow_y = shoulder_y + arm_len * np.cos(angle_rad)
                elbow_z = 0.0
                # Wrist follows
                wrist_x = elbow_x + forearm_len * np.sin(angle_rad)
                wrist_y = elbow_y + forearm_len * np.cos(angle_rad)
                wrist_z = 0.0
                
            elif plane == "sagittal":
                # Flexion: Moving in YZ plane (X=fixed). 
                # Z increases forward (or decreases? MP: Z negative is forward towards camera?)
                # MP: Z is depth. negative=closer to camera. 
                # Flexion is raising arm forward.
                elbow_x = shoulder_x
                elbow_y = shoulder_y + arm_len * np.cos(angle_rad)
                elbow_z = shoulder_z - arm_len * np.sin(angle_rad) # Negative Z = forward
                
                wrist_x = elbow_x
                wrist_y = elbow_y + forearm_len * np.cos(angle_rad)
                wrist_z = elbow_z - forearm_len * np.sin(angle_rad)
                
            elif plane == "sagittal_neg":
                # Extension: Backward. Z positive.
                elbow_x = shoulder_x
                elbow_y = shoulder_y + arm_len * np.cos(angle_rad)
                elbow_z = shoulder_z + arm_len * np.sin(angle_rad) 
                
                wrist_x = elbow_x
                wrist_y = elbow_y + forearm_len * np.cos(angle_rad)
                wrist_z = elbow_z + forearm_len * np.sin(angle_rad)

            elif "rot" in plane:
                 # Rotation: Elbow at side (down), forearm rotates in XZ plane
                 # 0 deg = forward. 90 deg = side.
                 # Elbow fixed down
                 elbow_x = shoulder_x
                 elbow_y = shoulder_y + arm_len * 1.0 # Down
                 elbow_z = shoulder_z
                 
                 # Wrist moves in circle around elbow
                 # For internal/external, the angle is 0..90
                 eff_angle = np.radians(current_angle)
                 if "neg" in plane: # External
                     eff_angle = -eff_angle
                 
                 # Wrist at 90 deg bend
                 # If arm is down, forearm is usually forward (Z-)
                 # Rotation moves it to side (X+)
                 # Let's say 0 = hand forward. 90 = hand side.
                 wrist_y = elbow_y # Horizontal forearm
                 wrist_x = elbow_x + forearm_len * np.sin(eff_angle)
                 wrist_z = elbow_z - forearm_len * np.cos(eff_angle) 

            elif "transverse" in plane:
                # Horizontal Ab/Adduction
                elbow_y = shoulder_y
                elbow_x = shoulder_x + arm_len * np.cos(angle_rad)
                elbow_z = shoulder_z + arm_len * np.sin(angle_rad)
                
                wrist_y = elbow_y
                wrist_x = elbow_x + forearm_len * np.cos(angle_rad)
                wrist_z = elbow_z + forearm_len * np.sin(angle_rad)

            elif plane == "sagittal_arm":
                # Elbow Flexion. Upper arm down. Forearm bends forward/up.
                # 180 = straight. 90 = bent.
                # Elbow is fixed down
                # Wrist moves in YZ plane
                eff_angle = np.radians(current_angle)
                # Angle definitions vary. Let's assume 180 is straight down, 90 is forward.
                # MP: y is down. z- is forward.
                # Wrist relative to elbow:
                # y = cos(angle), z = sin(angle)
                wrist_x = elbow_x
                # If angle=180 (straight), wrist is below elbow.
                # If angle=90, wrist is forward (z-) or side? "Sagittal" means forward.
                wrist_y = elbow_y - forearm_len * np.cos(eff_angle) # simple approx
                wrist_z = elbow_z - forearm_len * np.sin(eff_angle) 

            # === LOWER BODY / OTHER ===
            
            # Hip/Knee/Ankle Defaults
            hip_x, hip_y = 0.5, 0.7
            knee_x = hip_x + 0.05
            knee_y = hip_y + 0.15
            ankle_x = knee_x + 0.05
            ankle_y = knee_y + 0.12
            
            if plane == "frontal_leg":
                 # Hip Abduction. Leg moves side.
                 # Thigh moves.
                 eff_angle = np.radians(current_angle)
                 # 0 = vertical. 90 = side.
                 # knee relative to hip
                 knee_x = hip_x + 0.2 * np.sin(eff_angle)
                 knee_y = hip_y + 0.2 * np.cos(eff_angle)
                 # Ankle follows
                 ankle_x = knee_x + 0.2 * np.sin(eff_angle)
                 ankle_y = knee_y + 0.2 * np.cos(eff_angle)

            if plane == "sagittal_leg":
                 # Knee Flexion. Hip fixed. Knee fixed. Ankle moves up/back.
                 # Angle 0 = straight. 90 = bent.
                 # Thigh fixed.
                 knee_x, knee_y = hip_x, hip_y + 0.2
                 # Shin moves
                 eff_angle = np.radians(current_angle)
                 ankle_x = knee_x # Approx
                 ankle_y = knee_y + 0.15 * np.cos(eff_angle) # shortening y
                 ankle_z = 0.15 * np.sin(eff_angle) # moving z back
                 
            # Set values
            # Shoulder
            idx = shoulder_idx * 4
            keypoints[idx] = shoulder_x
            keypoints[idx + 1] = shoulder_y
            keypoints[idx + 2] = shoulder_z
            keypoints[idx + 3] = 0.95
            
            # Elbow
            idx = elbow_idx * 4
            keypoints[idx] = elbow_x
            keypoints[idx + 1] = elbow_y
            keypoints[idx + 2] = elbow_z
            keypoints[idx + 3] = 0.95
            
            # Wrist
            idx = wrist_idx * 4
            keypoints[idx] = wrist_x
            keypoints[idx + 1] = wrist_y
            keypoints[idx + 2] = wrist_z
            keypoints[idx + 3] = 0.95
            
            # Hip/Knee/Ankle (Simplified, static unless leg exercise)
            keypoints[hip_idx*4 : hip_idx*4+4] = [hip_x, hip_y, 0, 0.95]
            keypoints[knee_idx*4 : knee_idx*4+4] = [knee_x, knee_y, 0, 0.95]
            keypoints[ankle_idx*4 : ankle_idx*4+4] = [ankle_x, ankle_y, 0, 0.95]
            
            keypoints_list.append(keypoints)
    
    return keypoints_list


def generate_exercise_features(keypoints_sequence):
    """
    Extract features from keypoint sequence.
    
    Args:
        keypoints_sequence: List of keypoint arrays
        
    Returns:
        Aggregated feature vector
    """
    # For now, return mean of keypoints as feature
    # In production, extract angles and other features
    if not keypoints_sequence:
        return [0.0] * (NUM_LANDMARKS * 4)
    
    # Average all keypoints across frames
    array = np.array(keypoints_sequence)
    mean_features = np.mean(array, axis=0).tolist()
    
    # Add variance for each coordinate
    var_features = np.var(array, axis=0).tolist()
    
    return mean_features + var_features


def generate_synthetic_data():
    """
    Generate synthetic training data for all shoulder exercises.
    
    Returns:
        tuple: (features_list, labels_list)
    """
    all_features = []
    all_labels = []
    
    print("=" * 60)
    print("GENERATING SHOULDER EXERCISE TRAINING DATA")
    print("=" * 60)
    
    for exercise_name, exercise_config in SHOULDER_EXERCISES.items():
        # print(f"Processing {exercise_name}...") # Reduced verbosity for import usage
        
        angles = exercise_config["angles"]
        repetitions = exercise_config["repetitions"]
        
        # Generate multiple variations
        for rep in range(repetitions):
            # Create angle sequence for this repetition
            angle_sequence = []
            for min_angle, max_angle, mid_angle in angles:
                # Smooth transition from min to max
                n_points = 20
                transition = np.linspace(min_angle, max_angle, n_points)
                angle_sequence.extend(transition)
            
            # Generate keypoints
            keypoints = generate_synthetic_keypoints(angle_sequence)
            
            # Extract features
            features = generate_exercise_features(keypoints)
            
            all_features.append(features)
            all_labels.append(exercise_name)
            
    return all_features, all_labels

def create_training_data(output_path="data/processed_keypoints/exercise_data.csv"):
    """
    Create synthetic training data and save to CSV.
    
    Args:
        output_path: Path to save training data CSV
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    all_features, all_labels = generate_synthetic_data()
    
    print(f"\n💾 Total samples: {len(all_features)}")
    print(f"📊 Exercises: {len(set(all_labels))}")
    
    # Write to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        # Create header
        header = []
        for i in range(NUM_LANDMARKS * 8):  # 4 for coords + 4 for variance
            header.append(f"feature_{i}")
        header.append("label")
        
        writer = csv.writer(f)
        writer.writerow(header)
        
        # Write data
        for features, label in zip(all_features, all_labels):
            row = features + [label]
            writer.writerow(row)
    
    print(f"\n✅ Training data saved to: {output_path}")
    print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TRAINING DATA SUMMARY")
    print("=" * 60)
    
    for exercise_name in SHOULDER_EXERCISES.keys():
        count = all_labels.count(exercise_name)
        print(f"  {exercise_name:.<40} {count} samples")
    
    print("=" * 60)


if __name__ == "__main__":
    create_training_data()
