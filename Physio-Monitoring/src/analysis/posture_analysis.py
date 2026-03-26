import math

def calculate_angle(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c

    ba = (ax - bx, ay - by)
    bc = (cx - bx, cy - by)

    dot = ba[0]*bc[0] + ba[1]*bc[1]
    mag_ba = math.hypot(*ba)
    mag_bc = math.hypot(*bc)

    if mag_ba * mag_bc == 0:
        return 0

    # numeric safety: clamp cosine to [-1, 1]
    cos_val = dot / (mag_ba * mag_bc)
    cos_val = max(-1.0, min(1.0, cos_val))
    angle = math.degrees(math.acos(cos_val))
    return angle

def elbow_flexion(shoulder, elbow, wrist):
    return calculate_angle(shoulder, elbow, wrist), True

def shoulder_abduction(elbow, shoulder, hip):
    return calculate_angle(elbow, shoulder, hip), True

def knee_flexion(hip, knee, ankle):
    return calculate_angle(hip, knee, ankle), True

def hip_abduction(shoulder, hip, knee):
    return calculate_angle(shoulder, hip, knee), True
