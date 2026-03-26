"""
Comprehensive test suite for biomechanics models - FIXED VERSION.
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
from src.analysis.angle_calculation import (
    calculate_angle, calculate_angle_3d,
    elbow_angle, knee_angle, hip_angle,
    shoulder_abduction_angle, shoulder_flexion_angle,
    shoulder_extension_angle
)
from src.repetition.rep_counter import RepCounter
from src.repetition.rep_counter_improved import RepCounterImproved
from src.utils.quality_score import QualityScore


class TestAngleCalculation:
    """Test joint angle computation accuracy"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_right_angles(self):
        """Test 90-degree angles"""
        # Right angle: vertical-to-horizontal
        a = (0, 0)
        b = (0, 1)  # Vertex
        c = (1, 1)
        
        angle = calculate_angle(a, b, c)
        expected = 90
        
        if abs(angle - expected) < 1:
            self.passed += 1
            print(f"✅ Right Angle Test: {angle:.2f}° (expected {expected}°)")
        else:
            self.failed += 1
            self.errors.append(f"Right angle test failed: got {angle:.2f}°, expected {expected}°")
            print(f"❌ Right Angle Test: {angle:.2f}° (expected {expected}°)")
    
    def test_straight_angles(self):
        """Test 180-degree angles (straight line)"""
        a = (0, 0)
        b = (1, 1)  # Vertex
        c = (2, 2)
        
        angle = calculate_angle(a, b, c)
        expected = 180
        
        if abs(angle - expected) < 1:
            self.passed += 1
            print(f"✅ Straight Angle Test: {angle:.2f}° (expected {expected}°)")
        else:
            self.failed += 1
            self.errors.append(f"Straight angle test failed: got {angle:.2f}°, expected {expected}°")
            print(f"❌ Straight Angle Test: {angle:.2f}° (expected {expected}°)")
    
    def test_elbow_flexion_angles(self):
        """Test realistic elbow flexion angles"""
        test_cases = [
            # (shoulder, elbow, wrist, expected_angle, description)
            ((0, 0), (1, 0), (2, 0), 180, "Fully extended arm"),  # Straight arm
            ((0, 0), (1, 0), (1, 1), 90, "90-degree flex"),       # Right angle
        ]
        
        for shoulder, elbow, wrist, expected, desc in test_cases:
            angle = elbow_angle(shoulder, elbow, wrist)
            if abs(angle - expected) < 5:
                self.passed += 1
                print(f"✅ Elbow Flexion - {desc}: {angle:.2f}° (expected {expected}°)")
            else:
                self.failed += 1
                self.errors.append(f"Elbow flexion ({desc}) failed: got {angle:.2f}°, expected {expected}°")
                print(f"❌ Elbow Flexion - {desc}: {angle:.2f}° (expected {expected}°)")


class TestRepetitionCountingOriginal:
    """Test original repetition counting for debugging"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_basic_rep_counting(self):
        """Test counting single repetition with original counter"""
        counter = RepCounter(min_angle=70, max_angle=140, movement_threshold=3)
        
        # Simulate one complete rep: extended → flexed → extended
        angles = [
            160,  # Start: extended
            150,
            145,
            140,  # At max threshold
            120,  # Flexed state
            90,
            70,   # At min threshold
            75,
            160,  # Back to fully extended
        ]
        
        print("  Original Counter - Angle sequence:", angles)
        for i, angle in enumerate(angles):
            counter.update(angle, posture_ok=True)
            state = counter.phase
            print(f"    Angle {angle:3.0f}° → Phase: {state}, Reps: {counter.reps}")
        
        expected_reps = 1
        if counter.reps == expected_reps:
            self.passed += 1
            print(f"✅ Original Counter - Basic Rep: {counter.reps} reps")
        else:
            self.failed += 1
            self.errors.append(f"Original counter basic rep failed: got {counter.reps}, expected {expected_reps}")
            print(f"❌ Original Counter - Basic Rep: {counter.reps} reps (expected {expected_reps})")


class TestRepetitionCountingImproved:
    """Test improved repetition counting accuracy"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_basic_rep_counting(self):
        """Test counting single repetition"""
        counter = RepCounterImproved(min_angle=70, max_angle=140, movement_threshold=3)
        
        # Simulate one complete rep: extended → flexed → extended
        angles = [
            160,  # Start: extended (above max_angle)
            150,
            145,
            140,  # At max threshold
            120,  # Flexed state (below max_angle)
            90,
            70,   # At min threshold
            75,
            160,  # Back to fully extended
        ]
        
        for angle in angles:
            counter.update(angle, posture_ok=True)
        
        expected_reps = 1
        if counter.reps == expected_reps:
            self.passed += 1
            print(f"✅ Improved Rep Count - Basic: {counter.reps} reps (expected {expected_reps})")
        else:
            self.failed += 1
            self.errors.append(f"Improved basic rep count failed: got {counter.reps}, expected {expected_reps}")
            print(f"❌ Improved Rep Count - Basic: {counter.reps} reps (expected {expected_reps})")
    
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
            print(f"✅ Improved Rep Count - Multiple: {counter.reps} reps (expected {expected_reps})")
        else:
            self.failed += 1
            self.errors.append(f"Improved multiple reps failed: got {counter.reps}, expected {expected_reps}")
            print(f"❌ Improved Rep Count - Multiple: {counter.reps} reps (expected {expected_reps})")
    
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
            print(f"✅ Improved Rep Count - Posture Check: {counter.reps} reps (expected {expected_reps})")
        else:
            self.failed += 1
            self.errors.append(f"Improved posture check failed: got {counter.reps}, expected {expected_reps}")
            print(f"❌ Improved Rep Count - Posture Check: {counter.reps} reps (expected {expected_reps})")
    
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
            print(f"✅ Improved Rep Count - Noise Immunity: {counter.reps} reps (expected {expected_reps})")
        else:
            self.failed += 1
            self.errors.append(f"Improved noise immunity failed: got {counter.reps}, expected {expected_reps}")
            print(f"❌ Improved Rep Count - Noise Immunity: {counter.reps} reps (expected {expected_reps})")


class TestQualityScoring:
    """Test exercise quality scoring"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_full_rom_smooth_motion(self):
        """Test high quality score for full ROM smooth motion"""
        scorer = QualityScore(min_angle=70, max_angle=140)
        
        # Smooth motion with full ROM
        angles = list(np.linspace(160, 70, 20)) + list(np.linspace(70, 160, 20))
        
        for angle in angles:
            scorer.update(angle)
        
        quality = scorer.compute()
        
        if quality >= 80:
            self.passed += 1
            print(f"✅ Quality Scoring - Full ROM Smooth: Quality {quality}/100 (>=80 expected)")
        else:
            self.failed += 1
            self.errors.append(f"Full ROM smooth motion failed: got {quality}/100, expected >=80")
            print(f"❌ Quality Scoring - Full ROM Smooth: Quality {quality}/100 (>=80 expected)")
    
    def test_limited_rom_lower_quality(self):
        """Test lower quality for limited ROM"""
        scorer = QualityScore(min_angle=70, max_angle=140)
        
        # Limited range of motion (only 20 degrees)
        angles = [110, 115, 120, 125, 120, 115, 110] * 4
        
        for angle in angles:
            scorer.update(angle)
        
        quality = scorer.compute()
        
        if quality < 60:
            self.passed += 1
            print(f"✅ Quality Scoring - Limited ROM: Quality {quality}/100 (<60 expected)")
        else:
            self.failed += 1
            self.errors.append(f"Limited ROM failed: got {quality}/100, expected <60")
            print(f"❌ Quality Scoring - Limited ROM: Quality {quality}/100 (<60 expected)")
    
    def test_jerky_motion_lower_quality(self):
        """Test lower quality for jerky motion"""
        scorer = QualityScore(min_angle=70, max_angle=140)
        
        # Jerky motion with sudden changes
        angles = [160, 140, 100, 80, 70, 75, 120, 150, 160, 100, 80, 70] * 2
        
        for angle in angles:
            scorer.update(angle)
        
        quality = scorer.compute()
        
        if quality < 70:
            self.passed += 1
            print(f"✅ Quality Scoring - Jerky Motion: Quality {quality}/100 (<70 expected)")
        else:
            self.failed += 1
            self.errors.append(f"Jerky motion failed: got {quality}/100, expected <70")
            print(f"❌ Quality Scoring - Jerky Motion: Quality {quality}/100 (<70 expected)")


def run_all_tests():
    """Run all biomechanics tests"""
    print("\n" + "="*70)
    print("🧪 BIOMECHANICS MODELS TEST SUITE - IMPROVED VERSION")
    print("="*70 + "\n")
    
    # Angle Calculation Tests
    print("📐 JOINT ANGLE COMPUTATION TESTS")
    print("-" * 70)
    angle_tests = TestAngleCalculation()
    angle_tests.test_right_angles()
    angle_tests.test_straight_angles()
    angle_tests.test_elbow_flexion_angles()
    print(f"\nAngle Tests: {angle_tests.passed} passed, {angle_tests.failed} failed\n")
    
    # Original Repetition Counting Tests (for debugging)
    print("🔄 ORIGINAL REPETITION COUNTING (DEBUGGING)")
    print("-" * 70)
    orig_rep_tests = TestRepetitionCountingOriginal()
    orig_rep_tests.test_basic_rep_counting()
    print(f"\nOriginal Counter Tests: {orig_rep_tests.passed} passed, {orig_rep_tests.failed} failed\n")
    
    # Improved Repetition Counting Tests
    print("🔄 IMPROVED REPETITION COUNTING TESTS")
    print("-" * 70)
    rep_tests = TestRepetitionCountingImproved()
    rep_tests.test_basic_rep_counting()
    rep_tests.test_multiple_reps()
    rep_tests.test_posture_ignore_incorrect()
    rep_tests.test_noise_immunity()
    print(f"\nImproved Rep Tests: {rep_tests.passed} passed, {rep_tests.failed} failed\n")
    
    # Quality Scoring Tests
    print("⭐ QUALITY SCORING TESTS")
    print("-" * 70)
    quality_tests = TestQualityScoring()
    quality_tests.test_full_rom_smooth_motion()
    quality_tests.test_limited_rom_lower_quality()
    quality_tests.test_jerky_motion_lower_quality()
    print(f"\nQuality Tests: {quality_tests.passed} passed, {quality_tests.failed} failed\n")
    
    # Summary
    total_passed = angle_tests.passed + orig_rep_tests.passed + rep_tests.passed + quality_tests.passed
    total_failed = angle_tests.failed + orig_rep_tests.failed + rep_tests.failed + quality_tests.failed
    
    print("="*70)
    print("📊 OVERALL RESULTS")
    print("="*70)
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%")
    
    if total_failed > 0:
        print("\n❌ ISSUES FOUND:")
        all_errors = angle_tests.errors + rep_tests.errors + quality_tests.errors
        for error in all_errors:
            print(f"  - {error}")
        
        print("\n📋 RECOMMENDATIONS:")
        if orig_rep_tests.failed > 0:
            print("  ✓ Original RepCounter has logic errors → Use ImprovedRepCounter instead")
        if angle_tests.failed > 0:
            print("  ✓ Some angle calculation edge cases need review")
    else:
        print("\n✅ All biomechanics models are working accurately!")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
