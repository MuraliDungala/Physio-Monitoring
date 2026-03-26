"""
Debug script to test shoulder angle computation and rep counting in the backend engine
"""
import sys
import os

# Add paths
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Physio-Monitoring'))

from exercise_engine.engine import ExerciseEngine
from exercise_state_manager import ExerciseStateManager
import numpy as np

def create_mock_landmarks_shoulder_flexion(angle):
    """Create mock landmarks for shoulder flexion at specified angle"""
    # Simulate a shoulder flexion movement
    # angle: 0-180 where 0 is arm down, 180 is arm fully raised
    
    # Base positions
    landmarks = []
    
    # Nose (0)
    landmarks.append(type('obj', (object,), {'x': 0.5, 'y': 0.4, 'z': 0, 'visibility': 0.9})())
    
    # Fill indices 1-6 with dummy data
    for i in range(1, 7):
        landmarks.append(type('obj', (object,), {'x': 0.5, 'y': 0.5, 'z': 0, 'visibility': 0.9})())
    
    # Ears (7-8)
    landmarks.append(type('obj', (object,), {'x': 0.3, 'y': 0.3, 'z': 0, 'visibility': 0.9})())  # left ear
    landmarks.append(type('obj', (object,), {'x': 0.7, 'y': 0.3, 'z': 0, 'visibility': 0.9})())  # right ear
    
    # More dummy data (9-10)
    for i in range(2):
        landmarks.append(type('obj', (object,), {'x': 0.5, 'y': 0.5, 'z': 0, 'visibility': 0.9})())
    
    # Right shoulder (11)
    landmarks.append(type('obj', (object,), {'x': 0.6, 'y': 0.3, 'z': 0, 'visibility': 0.9})())
    
    # Left shoulder (12) 
    landmarks.append(type('obj', (object,), {'x': 0.4, 'y': 0.3, 'z': 0, 'visibility': 0.9})())
    
    # Right elbow (13) - moves based on flexion angle
    # At angle=0: elbow at (0.63, 0.5)
    # At angle=180: elbow at (0.6, 0.1)
    elbow_y = 0.5 - (angle / 180) * 0.4
    elbow_x = 0.63 + (angle / 180) * 0.05
    landmarks.append(type('obj', (object,), {'x': elbow_x, 'y': elbow_y, 'z': 0, 'visibility': 0.9})())
    
    # Left elbow (14)
    landmarks.append(type('obj', (object,), {'x': 0.37, 'y': elbow_y, 'z': 0, 'visibility': 0.9})())
    
    # Right wrist (15) - moves based on angle
    wrist_y = elbow_y - 0.1 * (angle / 180)
    wrist_x = elbow_x
    landmarks.append(type('obj', (object,), {'x': wrist_x, 'y': wrist_y, 'z': 0, 'visibility': 0.9})())
    
    # Left wrist (16)
    landmarks.append(type('obj', (object,), {'x': 0.37, 'y': wrist_y, 'z': 0, 'visibility': 0.9})())
    
    # Dummy data (17-21)
    for i in range(5):
        landmarks.append(type('obj', (object,), {'x': 0.5, 'y': 0.5, 'z': 0, 'visibility': 0.9})())
    
    # Left pinky (21), Right pinky (22)
    landmarks[21] = type('obj', (object,), {'x': 0.35, 'y': wrist_y, 'z': 0, 'visibility': 0.9})()
    landmarks.append(type('obj', (object,), {'x': 0.65, 'y': wrist_y, 'z': 0, 'visibility': 0.9})())
    
    # Left hip (23), Right hip (24)
    landmarks.append(type('obj', (object,), {'x': 0.4, 'y': 0.7, 'z': 0, 'visibility': 0.9})())  # left hip
    landmarks.append(type('obj', (object,), {'x': 0.6, 'y': 0.7, 'z': 0, 'visibility': 0.9})())  # right hip
    
    # Left knee (25), Right knee (26)
    landmarks.append(type('obj', (object,), {'x': 0.4, 'y': 0.9, 'z': 0, 'visibility': 0.9})())  # left knee
    landmarks.append(type('obj', (object,), {'x': 0.6, 'y': 0.9, 'z': 0, 'visibility': 0.9})())  # right knee
    
    # Left ankle (27), Right ankle (28)
    landmarks.append(type('obj', (object,), {'x': 0.4, 'y': 1.0, 'z': 0, 'visibility': 0.9})())  # left ankle
    landmarks.append(type('obj', (object,), {'x': 0.6, 'y': 1.0, 'z': 0, 'visibility': 0.9})())  # right ankle
    
    # Left index (29), Right index (30) - add them
    landmarks.append(type('obj', (object,), {'x': 0.65, 'y': wrist_y, 'z': 0, 'visibility': 0.9})())  # 29 - right index
    landmarks.append(type('obj', (object,), {'x': 0.35, 'y': wrist_y, 'z': 0, 'visibility': 0.9})())  # 30 - left index
    
    # Add more dummy landmarks to reach 33
    for i in range(33 - len(landmarks)):
        landmarks.append(type('obj', (object,), {'x': 0.5, 'y': 0.5, 'z': 0, 'visibility': 0.5})())
    
    return landmarks

def test_shoulder_flexion_angles():
    """Test if shoulder flexion angles are computed correctly"""
    print("\n" + "="*70)
    print("TEST 1: Shoulder Flexion Angle Computation")
    print("="*70)
    
    engine = ExerciseEngine()
    
    # Test with several angles
    test_angles = [20, 50, 100, 150, 180]
    
    for test_angle in test_angles:
        landmarks = create_mock_landmarks_shoulder_flexion(test_angle)
        coords, angles, motion = engine._extract_pose_data(landmarks)
        
        print(f"\nTest angle: {test_angle}°")
        print(f"  Coordinates found: {len(coords)}")
        print(f"  Angles computed: {list(angles.keys())}")
        
        if 'shoulder_flexion' in angles:
            print(f"  ✓ shoulder_flexion: {angles['shoulder_flexion']:.1f}°")
        else:
            print(f"  ✗ shoulder_flexion: NOT COMPUTED")
            if angles:
                print(f"    Available angles: {angles}")
        
        if 'right_elbow' in angles:
            print(f"  ✓ right_elbow: {angles['right_elbow']:.1f}°")

def test_rep_counting_shoulder():
    """Test rep counting for shoulder flexion"""
    print("\n" + "="*70)
    print("TEST 2: Rep Counting - Shoulder Flexion vs Elbow Flexion (UPDATED)")
    print("="*70)
    
    engine = ExerciseEngine()
    
    # Test shoulder flexion with NEW ranges: (20, 170)
    print("\n--- SHOULDER FLEXION (Range: 20-170) ---")
    state_shoulder = {'reps': 0, 'last_angle': 0, 'direction': None, 'counting': False}
    
    # Simulate arm movement: resting (15°) -> raised (90°) -> resting (15°) = 1 rep
    angles_to_test = [15, 30, 50, 70, 90, 110, 90, 70, 50, 30, 15]
    
    print("Angle sequence:", angles_to_test)
    for i, angle in enumerate(angles_to_test):
        prev_reps = state_shoulder['reps']
        reps, msg = engine._count_reps_simple("Shoulder Flexion", angle, state_shoulder)
        if state_shoulder['direction'] or reps > prev_reps or i == 0:
            print(f"  Frame {i:2d}: angle={angle:3.0f}° → reps={reps}, counting={state_shoulder['counting']}, direction={state_shoulder['direction']}, msg='{msg}'")
    
    print(f"\n✓ Result: {state_shoulder['reps']} reps (Shoulder)")
    if state_shoulder['reps'] == 1:
        print("  ✅ SHOULDER FLEXION WORKING")
    else:
        print("  ❌ SHOULDER FLEXION NOT COUNTING CORRECTLY")
    
    # Test elbow flexion with ranges: (30, 150)
    print("\n--- ELBOW FLEXION (Range: 30-150) ---")
    state_elbow = {'reps': 0, 'last_angle': 0, 'direction': None, 'counting': False}
    
    # Simulate elbow movement similar to shoulder
    angles_to_test = [20, 40, 60, 90, 130, 150, 130, 90, 60, 40, 20]
    
    print("Angle sequence:", angles_to_test)
    for i, angle in enumerate(angles_to_test):
        prev_reps = state_elbow['reps']
        reps, msg = engine._count_reps_simple("Elbow Flexion", angle, state_elbow)
        if state_elbow['direction'] or reps > prev_reps or i == 0:
            print(f"  Frame {i:2d}: angle={angle:3.0f}° → reps={reps}, counting={state_elbow['counting']}, direction={state_elbow['direction']}, msg='{msg}'")
    
    print(f"\n✓ Result: {state_elbow['reps']} reps (Elbow)")
    if state_elbow['reps'] == 1:
        print("  ✅ ELBOW FLEXION WORKING")
    else:
        print("  ❌ ELBOW FLEXION NOT COUNTING CORRECTLY")

def test_switching_exercises():
    """Test switching between elbow and shoulder exercises"""
    print("\n" + "="*70)
    print("TEST 3: Exercise Switching (Elbow -> Shoulder)")
    print("="*70)
    
    engine = ExerciseEngine()
    
    # First do some elbow flexion
    print("\n--- Phase 1: Elbow Flexion ---")
    for i, angle in enumerate([30, 60, 100, 135, 100, 60, 35, 30]):
        result = engine._track_selected_exercise(
            "Elbow Flexion",
            angle,
            {},
            {"reps": 0, "angle": 0, "posture_message": ""}
        )
        if i % 2 == 0:
            print(f"  Frame {i}: angle={angle}° → reps={result['reps']}")
    
    # Now switch to shoulder flexion
    print("\n--- Phase 2: Switch to Shoulder Flexion ---")
    # Reset should happen on frontend, let's simulate an intermediate state
    print("⚠️  Switching exercises - state should reset")
    
    for i, angle in enumerate([20, 50, 100, 150, 100, 50, 20]):
        result = engine._track_selected_exercise(
            "Shoulder Flexion",
            angle,
            {},
            {"reps": 0, "angle": 0, "posture_message": ""}
        )
        print(f"  Frame {i}: angle={angle}° → reps={result['reps']}, msg='{result['posture_message']}'")

if __name__ == "__main__":
    print("🔍 SHOULDER REP COUNTING DEBUG")
    print("Testing angle computation and rep counting logic\n")
    
    try:
        test_shoulder_flexion_angles()
        test_rep_counting_shoulder()
        test_switching_exercises()
        
        print("\n" + "="*70)
        print("✅ DEBUG TESTS COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
