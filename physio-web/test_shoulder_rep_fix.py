"""
Test script to verify shoulder and elbow rep counting after fixes
"""
import sys
import os

# Add paths
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Physio-Monitoring'))

from exercise_engine.engine import ExerciseEngine

def test_shoulder_rep_counting():
    """Test rep counting for shoulder flexion with NEW ranges"""
    print("\n" + "="*70)
    print("TEST: Shoulder Flexion Rep Counting (Range: 20-170)")
    print("="*70)
    
    engine = ExerciseEngine()
    state_shoulder = {'reps': 0, 'last_angle': 0, 'direction': None, 'counting': False}
    
    # Simulate arm movement: resting (15) -> raised (90) -> resting (15) = 1 rep
    angles_to_test = [15, 30, 50, 70, 90, 110, 90, 70, 50, 30, 15]
    
    print(f"Angle sequence: {angles_to_test}")
    prev_reps = 0
    for i, angle in enumerate(angles_to_test):
        reps, msg = engine._count_reps_simple("Shoulder Flexion", angle, state_shoulder)
        if reps > prev_reps or state_shoulder['direction'] or i == 0:
            print(f"  Frame {i:2d}: {angle:3d}deg -> reps={reps}, dir={state_shoulder.get('direction')}")
        prev_reps = reps
    
    print(f"\nResult: {state_shoulder['reps']} reps")
    if state_shoulder['reps'] == 1:
        print("SUCCESS: Shoulder rep counting works!")
        return True
    else:
        print("FAILED: Expected 1 rep, got " + str(state_shoulder['reps']))
        return False

def test_elbow_rep_counting():
    """Test rep counting for elbow flexion with existing ranges"""
    print("\n" + "="*70)
    print("TEST: Elbow Flexion Rep Counting (Range: 30-150)")
    print("="*70)
    
    engine = ExerciseEngine()
    state_elbow = {'reps': 0, 'last_angle': 0, 'direction': None, 'counting': False}
    
    # Simulate elbow movement
    angles_to_test = [20, 40, 60, 90, 130, 150, 130, 90, 60, 40, 20]
    
    print(f"Angle sequence: {angles_to_test}")
    prev_reps = 0
    for i, angle in enumerate(angles_to_test):
        reps, msg = engine._count_reps_simple("Elbow Flexion", angle, state_elbow)
        if reps > prev_reps or state_elbow['direction'] or i == 0:
            print(f"  Frame {i:2d}: {angle:3d}deg -> reps={reps}, dir={state_elbow.get('direction')}")
        prev_reps = reps
    
    print(f"\nResult: {state_elbow['reps']} reps")
    if state_elbow['reps'] == 1:
        print("SUCCESS: Elbow rep counting works!")
        return True
    else:
        print("FAILED: Expected 1 rep, got " + str(state_elbow['reps']))
        return False

def test_switching_exercises():
    """Test that both exercises can count reps independently"""
    print("\n" + "="*70)
    print("TEST: Multiple complete reps for both exercises")
    print("="*70)
    
    engine = ExerciseEngine()
    
    # Test shoulder with 2 reps
    print("\nShoulder Flexion - 2 complete reps:")
    state = {'reps': 0, 'last_angle': 0, 'direction': None, 'counting': False}
    angles = [15, 50, 100, 50, 15, 30, 80, 100, 80, 30, 15]  # 2 reps
    
    for angle in angles:
        reps, _ = engine._count_reps_simple("Shoulder Flexion", angle, state)
    
    print(f"  Result: {reps} reps")
    shoulder_pass = reps == 2
    
    # Test elbow with 2 reps
    print("\nElbow Flexion - 2 complete reps:")
    state = {'reps': 0, 'last_angle': 0, 'direction': None, 'counting': False}
    angles = [20, 50, 120, 50, 20, 40, 100, 140, 100, 40, 20]  # 2 reps
    
    for angle in angles:
        reps, _ = engine._count_reps_simple("Elbow Flexion", angle, state)
    
    print(f"  Result: {reps} reps")
    elbow_pass = reps == 2
    
    if shoulder_pass and elbow_pass:
        print("\nSUCCESS: Both exercises can count multiple reps!")
        return True
    else:
        print(f"\nFAILED: Shoulder={shoulder_pass}, Elbow={elbow_pass}")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SHOULDER REP COUNTING - VERIFICATION TESTS")
    print("="*70)
    
    try:
        results = []
        results.append(("Shoulder Rep Counting", test_shoulder_rep_counting()))
        results.append(("Elbow Rep Counting", test_elbow_rep_counting()))
        results.append(("Multiple Reps", test_switching_exercises()))
        
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        for name, passed in results:
            status = "PASS" if passed else "FAIL"
            print(f"{name:.<50} {status}")
        
        all_pass = all(r[1] for r in results)
        if all_pass:
            print("\nAll tests PASSED! The fix is working.")
        else:
            print("\nSome tests FAILED. More investigation needed.")
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
