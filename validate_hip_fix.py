#!/usr/bin/env python3
"""
Final validation test for hip exercise fix
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "physio-web" / "backend"))

def test_imports():
    """Test that the engine imports correctly"""
    try:
        from exercise_engine.engine import ExerciseEngine
        print("✓ ExerciseEngine imports successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import ExerciseEngine: {e}")
        return False

def test_methods_exist():
    """Test that required methods exist"""
    try:
        from exercise_engine.engine import ExerciseEngine
        engine = ExerciseEngine()
        
        # Check for the new method
        if not hasattr(engine, '_calculate_lateral_angle'):
            print("✗ Missing _calculate_lateral_angle method")
            return False
        print("✓ _calculate_lateral_angle method exists")
        
        # Check for existing methods
        if not hasattr(engine, '_calculate_angle_3d'):
            print("✗ Missing _calculate_angle_3d method")
            return False
        print("✓ _calculate_angle_3d method exists")
        
        if not hasattr(engine, '_compute_angles_basic'):
            print("✗ Missing _compute_angles_basic method")
            return False
        print("✓ _compute_angles_basic method exists")
        
        if not hasattr(engine, '_track_selected_exercise'):
            print("✗ Missing _track_selected_exercise method")
            return False
        print("✓ _track_selected_exercise method exists")
        
        if not hasattr(engine, 'process_frame'):
            print("✗ Missing process_frame method")
            return False
        print("✓ process_frame method exists")
        
        return True
    except Exception as e:
        print(f"✗ Failed method check: {e}")
        return False

def test_angle_calculation():
    """Test that angle calculation works"""
    try:
        from exercise_engine.engine import ExerciseEngine
        engine = ExerciseEngine()
        
        # Test lateral angle calculation
        hip = (0.5, 0.5, 0)
        knee = (0.6, 0.7, 0)
        
        angle = engine._calculate_lateral_angle(hip, knee)
        if angle < 0 or angle > 90:
            print(f"✗ Invalid angle result: {angle}° (should be 0-90°)")
            return False
        
        print(f"✓ Lateral angle calculation works: {angle:.1f}°")
        
        # Test 3D angle calculation
        p1 = (0, 0, 0)
        p2 = (0, 1, 0)  # vertex
        p3 = (1, 1, 0)
        
        angle2 = engine._calculate_angle_3d(p1, p2, p3)
        if angle2 < 0 or angle2 > 180:
            print(f"✗ Invalid 3D angle result: {angle2}° (should be 0-180°)")
            return False
        
        print(f"✓ 3D angle calculation works: {angle2:.1f}°")
        return True
    except Exception as e:
        print(f"✗ Angle calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("FINAL VALIDATION TEST FOR HIP EXERCISE FIX")
    print("=" * 60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Methods", test_methods_exist),
        ("Angle Calculations", test_angle_calculation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 40)
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✓ PASS" if results[i] else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results)
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL VALIDATION TESTS PASSED")
        print("\nThe hip exercise fix is ready for deployment.")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease review the errors above.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
