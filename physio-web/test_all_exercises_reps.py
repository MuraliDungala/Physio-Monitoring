"""
Test rep counting for ALL exercise types to ensure comprehensive coverage
"""
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Physio-Monitoring'))

from exercise_engine.engine import ExerciseEngine

def test_all_exercises():
    """Test rep counting for all exercise types"""
    print("\n" + "="*70)
    print("COMPREHENSIVE REP COUNTING TEST - ALL EXERCISES")
    print("="*70)
    
    engine = ExerciseEngine()
    
    # Define test cases for each exercise type
    # Format: exercise_name: (angle_sequence, expected_reps)
    test_cases = {
        # Neck exercises
        'Neck Flexion': ([10, 20, 30, 40, 50, 40, 30, 20, 10], 1),
        'Neck Extension': ([50, 40, 30, 20, 10, 20, 30, 40, 50], 1),
        'Neck Rotation': ([10, 30, 60, 80, 60, 30, 10], 1),
        
        # Shoulder exercises
        'Shoulder Flexion': ([15, 30, 50, 90, 120, 90, 50, 30, 15], 1),
        'Shoulder Extension': ([5, 15, 40, 55, 40, 15, 5], 1),
        'Shoulder Abduction': ([20, 40, 70, 110, 70, 40, 20], 1),
        'Shoulder Adduction': ([5, 20, 40, 55, 40, 20, 5], 1),
        
        # Elbow exercises
        'Elbow Flexion': ([30, 50, 100, 150, 100, 50, 30], 1),
        'Elbow Extension': ([160, 140, 100, 70, 100, 140, 160], 1),
        
        # Knee exercises
        'Knee Flexion': ([30, 50, 90, 140, 90, 50, 30], 1),
        'Knee Extension': ([160, 150, 120, 80, 120, 150, 160], 1),
        
        # Hip exercises
        'Hip Abduction': ([15, 25, 40, 60, 40, 25, 15], 1),
        'Hip Flexion': ([25, 40, 65, 90, 65, 40, 25], 1),
        
        # Wrist exercises
        'Wrist Flexion': ([20, 35, 55, 80, 55, 35, 20], 1),
        'Wrist Extension': ([80, 55, 35, 20, 35, 55, 80], 1),
        
        # Back exercises
        'Back Extension': ([5, 15, 30, 45, 30, 15, 5], 1),
        
        # Ankle exercises
        'Ankle Dorsiflexion': ([70, 85, 110, 120, 110, 85, 70], 1),
        'Ankle Plantarflexion': ([80, 100, 130, 160, 130, 100, 80], 1),
    }
    
    results = {}
    
    for exercise, (angles, expected_reps) in test_cases.items():
        state = {'reps': 0, 'last_angle': 0, 'direction': None, 'counting': False}
        
        for angle in angles:
            reps, _ = engine._count_reps_simple(exercise, angle, state)
        
        actual_reps = reps
        passed = actual_reps == expected_reps
        results[exercise] = passed
        
        status = "PASS" if passed else "FAIL"
        print(f"{exercise:.<50} {status:>6} (got {actual_reps}, expected {expected_reps})")
    
    # Summary
    total = len(results)
    passed_count = sum(1 for v in results.values() if v)
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed_count}/{total} exercises passing")
    print("="*70)
    
    if passed_count == total:
        print("\n✅ SUCCESS: ALL EXERCISES COUNT REPS CORRECTLY!")
    else:
        print(f"\n❌ {total - passed_count} exercises need attention")
        failing = [k for k, v in results.items() if not v]
        print("Failing exercises:", ", ".join(failing))
    
    return passed_count == total

if __name__ == "__main__":
    try:
        success = test_all_exercises()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
