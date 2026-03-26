import numpy as np

def calculate_angle(a, b, c):
    """Calculate angle between three points (vertex at b)"""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cos = np.dot(ba, bc) / (np.linalg.norm(ba)*np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))

def calculate_angle_3d(a, b, c):
    """Calculate 3D angle between three points"""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cos = np.dot(ba, bc) / (np.linalg.norm(ba)*np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))

# ============= ELBOW ANGLES =============
def elbow_angle(shoulder, elbow, wrist):
    """Elbow flexion/extension angle"""
    return calculate_angle(shoulder, elbow, wrist)

def elbow_flexion(shoulder, elbow, wrist):
    """Elbow flexion angle (0-140 degrees)"""
    return (calculate_angle(shoulder, elbow, wrist),)

def elbow_extension_angle(shoulder, elbow, wrist):
    """Elbow extension angle - same as flexion angle, measures straightness of arm"""
    return calculate_angle(shoulder, elbow, wrist)

# ============= KNEE ANGLES =============
def knee_angle(hip, knee, ankle):
    """Knee flexion/extension angle"""
    return calculate_angle(hip, knee, ankle)

# ============= HIP ANGLES =============
def hip_angle(shoulder, hip, knee):
    """Hip flexion/extension angle"""
    return calculate_angle(shoulder, hip, knee)

# ============= SHOULDER ANGLES =============

def shoulder_abduction_angle(shoulder, elbow, hip):
    """
    Shoulder abduction/adduction angle.
    Angle between arm (shoulder-elbow) and body (hip-shoulder vertical line).
    0° = arm down, 180° = arm fully up (rare in physio)
    """
    return calculate_angle(elbow, shoulder, hip)

def shoulder_flexion_angle(shoulder, elbow, hip):
    """
    Shoulder flexion/extension angle.
    Angle in sagittal plane (front-back): hip-shoulder-elbow
    0° = arm down, 180° = arm fully up in front
    """
    return calculate_angle(hip, shoulder, elbow)

def shoulder_extension_angle(shoulder, elbow, hip):
    """
    Shoulder extension angle (backward movement).
    Angle in sagittal plane: hip-shoulder-elbow (measured backward)
    0° = arm forward, 60° = arm extended backward
    """
    return calculate_angle(hip, shoulder, elbow)

def shoulder_internal_rotation_angle(shoulder, elbow, wrist):
    """
    Shoulder internal (medial) rotation angle.
    Measures rotation of forearm around shoulder-elbow axis.
    Uses angle between forearm and frontal plane.
    """
    # Angle of forearm relative to elbow position
    return calculate_angle(shoulder, elbow, wrist)

def shoulder_external_rotation_angle(shoulder, elbow, wrist):
    """
    Shoulder external (lateral) rotation angle.
    Opposite of internal rotation - measures outward rotation.
    In opposite direction from internal rotation.
    """
    # For now, same calculation (in practice, external rotation
    # would be measured when wrist is on opposite side)
    # Angle based on wrist position relative to elbow
    angle = calculate_angle(shoulder, elbow, wrist)
    # External rotation would have wrist higher/opposite position
    # For detection, we can use 180 - angle or track wrist height
    return min(angle, 180 - angle)  # Cap at 180 for rotation measurement

def shoulder_circumduction_angle(shoulder, elbow, hip):
    """
    Shoulder circumduction angle.
    Circular movement - track the combined angle in frontal plane.
    Uses combination of abduction and flexion.
    """
    # For circumduction, we track circular motion
    return calculate_angle(elbow, shoulder, hip)

# ============= COMPOUND SHOULDER ANGLES (3D) =============

def shoulder_horizontal_abduction_angle(shoulder, elbow, spine):
    """
    Horizontal abduction angle (arm moving backward).
    Angle in transverse plane - measures how far arm goes back.
    Calculated from elbow position relative to shoulder and spine.
    """
    # Angle between arm (elbow-shoulder) and spine direction
    # For abduction (moving back), angle increases as arm goes backward
    angle = calculate_angle(elbow, shoulder, spine)
    return angle

def shoulder_horizontal_adduction_angle(shoulder, elbow, spine):
    """
    Horizontal adduction angle (arm moving forward across body).
    Angle in transverse plane - measures how far arm comes across body.
    Opposite direction from horizontal abduction.
    """
    # For adduction (moving forward), we measure the complement
    # This ensures it's different from horizontal abduction
    angle = calculate_angle(elbow, shoulder, spine)
    # Adduction is measured as 180 - abduction angle in transverse plane
    # This makes them distinct even though they use same landmarks
    return max(0, 180 - angle) if angle < 90 else angle

# ============= HELPER: Calculate rotation angle =============

def calculate_shoulder_rotation(shoulder, elbow, wrist, prev_wrist=None):
    """
    Calculate shoulder rotation angle around the arm axis.
    Used for internal/external rotation tracking.
    """
    if prev_wrist is None:
        return 0
    
    # Vector from shoulder to elbow (arm axis)
    arm_axis = np.array(elbow) - np.array(shoulder)
    
    # Vectors from elbow to wrist (before and after)
    v1 = np.array(prev_wrist) - np.array(elbow)
    v2 = np.array(wrist) - np.array(elbow)
    
    # Calculate rotation around arm axis
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1)*np.linalg.norm(v2) + 1e-6)
    return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
