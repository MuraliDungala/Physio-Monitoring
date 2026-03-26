import os

# Base paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
EXTERNAL_DATA_DIR = os.path.join(DATA_DIR, "external")

# Dataset specific paths
UI_PMRD_PATH = os.path.join(EXTERNAL_DATA_DIR, "UI-PMRD")
KIMORE_PATH = os.path.join(EXTERNAL_DATA_DIR, "KIMORE")

# Mapping from external dataset labels to internal exercise names
# Internal names: 
# "Shoulder Flexion", "Shoulder Extension", "Shoulder Abduction", "Shoulder Adduction",
# "Shoulder Internal Rotation", "Shoulder External Rotation", 
# "Shoulder Horizontal Abduction", "Shoulder Horizontal Adduction", "Shoulder Circumduction",
# "Elbow Flexion", "Elbow Extension", "Knee Flexion", "Hip Abduction"

# UI-PMRD has 10 movements. Mapping based on standard rehabilitation protocols.
# Note: Actual file names/labels in UI-PMRD need to be inspected. 
# This is a best-effort mapping assuming standard naming or indices.
UI_PMRD_MAPPING = {
    "m01": "Shoulder Abduction",
    "m02": "Shoulder Adduction",
    "m03": "Shoulder Flexion",
    "m04": "Shoulder Extension",
    "m05": "Shoulder Internal Rotation",
    "m06": "Shoulder External Rotation",
    "m07": "Elbow Flexion",
    "m08": "Elbow Extension",
    # m09, m10 might be other exercises, mapped if applicable
}

# KIMORE exercises:
# Ex1: Arm lifting (Shoulder Flexion/Abduction)
# Ex2: Lateral trunk tilt (Not supported directly, maybe Hip Abduction context)
# Ex3: Trunk rotation
# Ex4: Pelvis rotations
# Ex5: Squatting (Knee Flexion context)
KIMORE_MAPPING = {
    "Ex1": "Shoulder Flexion",
    "Es1": "Shoulder Flexion",
    "Ex5": "Knee Flexion",
    "Es5": "Knee Flexion",
}
