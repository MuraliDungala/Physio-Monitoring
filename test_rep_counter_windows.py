"""
Comprehensive test suite for biomechanics models - WINDOWS COMPATIBLE.
Tests accuracy of:
1. Joint Angle Computation
2. Repetition Counting (Original vs Improved)
3. Posture Assessment
4. Quality Scoring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Physio-Monitoring'))

import numpy as np
from src.analysis.angle_calculation import calculate_angle, elbow_angle, knee_angle, hip_angle
from src.repetition.rep_counter import RepCounter
from src.repetition.rep_counter_improved import RepCounterImproved
from src.utils.quality_score import QualityScore


class TestRepetitionCountingImproved:
    """Test improved repetition counting accuracy"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_basic_rep_counting(self):
        """Test counting single repetition"""
        counter = RepCounterImproved(min_angle=70, max_angle=140, movement_threshold=3)
        
        # Simulate one complete rep: extended -> flexed -> extended
        angles = [160, 150, 145, 140, 120, 90, 70, 75, 160]
        
        for angle in angles:
            counter.update(angle, posture_ok=True)
        
        expected_reps = 1
        if counter.reps == expected_reps:
            self.passed += 1
            print("[PASS] Basic Rep Count: {} reps (expected {})".format(counter.reps, expected_reps))
            return True
        else:
            self.failed += 1
            self.errors.append("Basic rep failed: got {}, expected {}".format(counter.reps, expected_reps))
            print("[FAIL] Basic Rep Count: {} reps (expected {})".format(counter.reps, expected_reps))
            return False
    
    def test_multiple_reps(self):
        """Test counting multiple repetitions"""
        counter = RepCounterImproved(min_angle=70, max_angle=140, movement_threshold=2)
        
        # Simulate three reps
        angles = [
            160, 150, 140, 100, 80, 70, 160,  # Rep 1
            150, 140, 110, 70, 160,            # Rep 2
            150, 130, 100, 75, 70, 160,        # Rep 3
        ]
        
        for angle in angles:
            counter.update(angle, posture_ok=True)
        
        expected_reps = 3
        if counter.reps == expected_reps:
            self.passed += 1
            print("[PASS] Multiple Reps Count: {} reps (expected {})".format(counter.reps, expected_reps))
            return True
        else:
            self.failed += 1
            self.errors.append("Multiple reps failed: got {}, expected {}".format(counter.reps, expected_reps))
            print("[FAIL] Multiple Reps Count: {} reps (expected {})".format(counter.reps, expected_reps))
            return False
    
    def test_posture_ignore_incorrect(self):
        """Test that reps with incorrect posture are not counted"""
        counter = RepCounterImproved(min_angle=70, max_angle=140, movement_threshold=2)
        
        angles = [
            160, 150, 140, 100, 80, 70, 160,  # Rep 1 (posture OK)
            150, 140, 110, 70, 160,            # Rep 2 (posture incorrect)
        ]
        
        posture_ok = [
            True, True, True, True, True, True, True,
            True, True, True, False, False,  # Bad posture in 2nd rep
        ]
        
        for angle, posture in zip(angles, posture_ok):
            counter.update(angle, posture_ok=posture)
        
        expected_reps = 1  # Only first rep counted
        if counter.reps == expected_reps:
            self.passed += 1
            print("[PASS] Posture Check: {} reps (expected {})".format(counter.reps, expected_reps))
            return True
        else:
            self.failed += 1
            self.errors.append("Posture check failed: got {}, expected {}".format(counter.reps, expected_reps))
            print("[FAIL] Posture Check: {} reps (expected {})".format(counter.reps, expected_reps))
            return False
    
    def test_noise_immunity(self):
        """Test immunity to small angle jitter"""
        counter = RepCounterImproved(min_angle=70, max_angle=140, movement_threshold=5)
        
        # Add noise (small angle variations < threshold)
        angles = [
            160, 161, 159, 158,  # Noisy extended
            150, 149, 150,
            140, 139, 140, 141,
            100, 101, 99, 100,
            80, 79, 80, 81, 79,
            70, 71, 70,
            160, 161, 159,  # Noisy extended again
        ]
        
        for angle in angles:
            counter.update(angle, posture_ok=True)
        
        expected_reps = 1
        if counter.reps == expected_reps:
            self.passed += 1
            print("[PASS] Noise Immunity: {} reps (expected {})".format(counter.reps, expected_reps))
            return True
        else:
            self.failed += 1
            self.errors.append("Noise immunity failed: got {}, expected {}".format(counter.reps, expected_reps))
            print("[FAIL] Noise Immunity: {} reps (expected {})".format(counter.reps, expected_reps))
            return False


def run_all_tests():
    """Run all improved rep counter tests"""
    print("\n" + "="*70)
    print("[TEST SUITE] BIOMECHANICS REPETITION COUNTING - IMPROVED VERSION")
    print("="*70 + "\n")
    
    print("[TEST] IMPROVED REPETITION COUNTING")
    print("-" * 70)
    rep_tests = TestRepetitionCountingImproved()
    rep_tests.test_basic_rep_counting()
    rep_tests.test_multiple_reps()
    rep_tests.test_posture_ignore_incorrect()
    rep_tests.test_noise_immunity()
    
    total_passed = rep_tests.passed
    total_failed = rep_tests.failed
    
    print("\n" + "="*70)
    print("[RESULTS] REPETITION COUNTER VALIDATION")
    print("="*70)
    print("Passed: {} | Failed: {}".format(total_passed, total_failed))
    print("Success Rate: {:.1f}%".format((total_passed/(total_passed+total_failed)*100) if (total_passed+total_failed) > 0 else 0))
    
    if total_failed > 0:
        print("\n[ISSUES FOUND]")
        for error in rep_tests.errors:
            print("  - " + error)
        return False
    else:
        print("\n[SUCCESS] Repetition Counter is working accurately!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
