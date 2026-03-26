#!/usr/bin/env python3
"""
Comprehensive Exercise Detection Accuracy Test

Tests the ML model's ability to correctly identify all 28 exercises
from pose data with varying confidence levels and scenarios.

Tests:
- Detection accuracy for each exercise
- Detection confidence scores
- False positive/negative rates
- Detection latency
- Multi-view detection (left/right symmetry)
"""

import sys
import os
import time
import numpy as np
from collections import defaultdict

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'physio-web', 'backend'))

from exercise_engine.engine import ExerciseEngine

# All 28 exercises to test
ALL_EXERCISES = [
    # Shoulder (6)
    "Shoulder Flexion",
    "Shoulder Extension", 
    "Shoulder Abduction",
    "Shoulder Adduction",
    "Shoulder Internal Rotation",
    "Shoulder External Rotation",
    
    # Elbow (2)
    "Elbow Flexion",
    "Elbow Extension",
    
    # Knee (2)
    "Knee Flexion",
    "Knee Extension",
    
    # Hip (2)
    "Hip Abduction",
    "Hip Flexion",
    
    # Neck (3)
    "Neck Flexion",
    "Neck Extension",
    "Neck Rotation",
    
    # Wrist (2)
    "Wrist Flexion",
    "Wrist Extension",
    
    # Ankle (5)
    "Ankle Dorsiflexion",
    "Ankle Plantarflexion",
    "Ankle Inversion",
    "Ankle Eversion",
    "Ankle Circles",
    
    # Squat (5)
    "Body Weight Squat",
    "Wall Sit",
    "Sumo Squat",
    "Partial Squat",
    "Squat Hold",
    
    # Back (1)
    "Back Extension",
]


class ExerciseDetectionTester:
    """Test exercise detection accuracy across all 28 exercises"""
    
    def __init__(self):
        self.engine = ExerciseEngine()
        self.results = {
            "detection_accuracy": defaultdict(dict),
            "confidence_scores": defaultdict(list),
            "detection_times": defaultdict(list),
            "false_positives": defaultdict(int),
            "false_negatives": defaultdict(int),
        }
        
    def create_mock_landmarks(self, exercise_name):
        """Create realistic landmark data for motion simulation"""
        # Create MediaPipe-compatible landmarks (NormalizedLandmark objects)
        # We'll return as list of tuples (x, y, z) that mimics MediaPipe format
        from types import SimpleNamespace
        
        # Create 33 landmarks (MediaPipe format)
        landmarks_array = np.zeros((33, 3))
        
        # Base pose (neutral standing position)
        landmarks_array = self._set_base_landmarks(landmarks_array)
        
        # Apply exercise-specific modifications
        landmarks_array = self._apply_exercise_motion(landmarks_array, exercise_name)
        
        # Convert to MediaPipe-style objects
        landmarks = []
        for i in range(33):
            lm = SimpleNamespace(
                x=float(landmarks_array[i, 0]),
                y=float(landmarks_array[i, 1]),
                z=float(landmarks_array[i, 2]),
                visibility=1.0
            )
            landmarks.append(lm)
        
        return landmarks
    
    def _set_base_landmarks(self, landmarks):
        """Set base neutral pose landmarks"""
        # Simplified neutral pose coordinates (normalized 0-1)
        base_pose = {
            # Body (0-10)
            0: [0.5, 0.1, 0.5],      # Nose
            1: [0.45, 0.08, 0.5],    # Left eye
            2: [0.55, 0.08, 0.5],    # Right eye
            3: [0.4, 0.08, 0.5],     # Left ear
            4: [0.6, 0.08, 0.5],     # Right ear
            5: [0.4, 0.2, 0.5],      # Left shoulder
            6: [0.6, 0.2, 0.5],      # Right shoulder
            7: [0.35, 0.4, 0.5],     # Left elbow
            8: [0.65, 0.4, 0.5],     # Right elbow
            9: [0.3, 0.6, 0.5],      # Left wrist
            10: [0.7, 0.6, 0.5],     # Right wrist
            
            # Lower body (11-16)
            11: [0.4, 0.5, 0.5],     # Left hip
            12: [0.6, 0.5, 0.5],     # Right hip
            13: [0.4, 0.75, 0.5],    # Left knee
            14: [0.6, 0.75, 0.5],    # Right knee
            15: [0.4, 1.0, 0.5],     # Left ankle
            16: [0.6, 1.0, 0.5],     # Right ankle
        }
        
        for idx, coord in base_pose.items():
            landmarks[idx] = coord
        
        return landmarks
    
    def _apply_exercise_motion(self, landmarks, exercise_name):
        """Apply exercise-specific motions to landmarks"""
        
        # Make a copy to modify
        lm = landmarks.copy()
        
        # Exercise-specific modifications (simulating active motion)
        if "Shoulder Flexion" in exercise_name:
            lm[9, 1] -= 0.15  # Left wrist up (flexion)
            lm[10, 1] -= 0.15 # Right wrist up
            
        elif "Shoulder Extension" in exercise_name:
            lm[9, 1] += 0.1   # Left wrist down (extension)
            lm[10, 1] += 0.1  # Right wrist down
            
        elif "Shoulder Abduction" in exercise_name:
            lm[7, 0] -= 0.15  # Left elbow out (abduction)
            lm[8, 0] += 0.15  # Right elbow out
            
        elif "Shoulder Adduction" in exercise_name:
            lm[7, 0] += 0.1   # Left elbow in (adduction)
            lm[8, 0] -= 0.1   # Right elbow in
            
        elif "Shoulder Internal Rotation" in exercise_name:
            lm[9, 0] += 0.1   # Left wrist rotated in
            lm[10, 0] -= 0.1  # Right wrist rotated in
            
        elif "Shoulder External Rotation" in exercise_name:
            lm[9, 0] -= 0.1   # Left wrist rotated out
            lm[10, 0] += 0.1  # Right wrist rotated out
            
        elif "Elbow Flexion" in exercise_name:
            lm[9, 1] -= 0.2   # Left wrist up (flexion)
            lm[10, 1] -= 0.2  # Right wrist up
            lm[7, 1] -= 0.1   # Elbow up
            lm[8, 1] -= 0.1
            
        elif "Elbow Extension" in exercise_name:
            lm[9, 1] += 0.15  # Left wrist down (extension)
            lm[10, 1] += 0.15 # Right wrist down
            
        elif "Knee Flexion" in exercise_name:
            lm[13, 1] -= 0.2  # Left knee up (flexion)
            lm[14, 1] -= 0.2  # Right knee up
            lm[15, 1] -= 0.2  # Ankle follows
            lm[16, 1] -= 0.2
            
        elif "Knee Extension" in exercise_name:
            lm[13, 1] += 0.15 # Left knee down (extension)
            lm[14, 1] += 0.15 # Right knee down
            
        elif "Hip Abduction" in exercise_name:
            lm[11, 0] -= 0.1  # Left hip out (abduction)
            lm[12, 0] += 0.1  # Right hip out
            lm[13, 0] -= 0.1  # Knee follows
            lm[14, 0] += 0.1
            
        elif "Hip Flexion" in exercise_name:
            lm[11, 1] -= 0.15 # Left hip up (flexion)
            lm[12, 1] -= 0.15 # Right hip up
            lm[13, 1] -= 0.15 # Knee follows
            lm[14, 1] -= 0.15
            
        elif "Neck Flexion" in exercise_name:
            lm[0, 1] += 0.08  # Nose down (flexion)
            
        elif "Neck Extension" in exercise_name:
            lm[0, 1] -= 0.08  # Nose up (extension)
            
        elif "Neck Rotation" in exercise_name:
            lm[0, 0] += 0.1   # Nose rotated right
            lm[1, 0] += 0.1   # Eyes follow
            lm[2, 0] += 0.1
            
        elif "Wrist Flexion" in exercise_name:
            lm[9, 1] -= 0.08  # Left wrist down (flexion)
            lm[10, 1] -= 0.08 # Right wrist down
            
        elif "Wrist Extension" in exercise_name:
            lm[9, 1] += 0.08  # Left wrist up (extension)
            lm[10, 1] += 0.08 # Right wrist up
            
        elif "Ankle Dorsiflexion" in exercise_name:
            lm[15, 1] -= 0.08 # Left ankle up (dorsiflexion)
            lm[16, 1] -= 0.08 # Right ankle up
            
        elif "Ankle Plantarflexion" in exercise_name:
            lm[15, 1] += 0.08 # Left ankle down (plantarflexion)
            lm[16, 1] += 0.08 # Right ankle down
            
        elif "Ankle Inversion" in exercise_name:
            lm[15, 0] += 0.06 # Left ankle in (inversion)
            lm[16, 0] -= 0.06 # Right ankle in
            
        elif "Ankle Eversion" in exercise_name:
            lm[15, 0] -= 0.06 # Left ankle out (eversion)
            lm[16, 0] += 0.06 # Right ankle out
            
        elif "Ankle Circles" in exercise_name:
            # Circular motion
            lm[15, 0] += 0.1  # Left ankle rotated
            lm[15, 1] += 0.08
            lm[16, 0] -= 0.1  # Right ankle rotated
            lm[16, 1] += 0.08
            
        elif "Body Weight Squat" in exercise_name or "Squat" in exercise_name:
            lm[11, 1] += 0.2  # Hips down (squat)
            lm[12, 1] += 0.2
            lm[13, 1] += 0.15 # Knees bend
            lm[14, 1] += 0.15
            
        elif "Back Extension" in exercise_name:
            lm[5, 1] -= 0.1   # Left shoulder back (extension)
            lm[6, 1] -= 0.1   # Right shoulder back
        
        return lm
    
    def test_exercise_detection(self, exercise_name, num_iterations=10):
        """Test detection accuracy for a single exercise"""
        
        if not self.engine.ml_predictor or not self.engine.ml_predictor.is_ready():
            return {
                "detected": False,
                "accuracy": 0,
                "avg_confidence": 0,
                "avg_latency": 0,
                "status": "ML model not available"
            }
        
        correct_detections = 0
        confidences = []
        latencies = []
        
        for i in range(num_iterations):
            # Create mock landmarks with exercise motion
            landmarks = self.create_mock_landmarks(exercise_name)
            
            # Test detection
            start_time = time.perf_counter()
            predicted_exercise, confidence = self.engine.ml_predictor.predict(
                landmarks, 
                confidence_threshold=0.0  # Get prediction regardless of threshold
            )
            latency = (time.perf_counter() - start_time) * 1000  # ms
            
            latencies.append(latency)
            
            if predicted_exercise:
                confidences.append(confidence)
                
                # Check for correct detection
                if predicted_exercise.lower() == exercise_name.lower():
                    correct_detections += 1
                else:
                    # Record false positive
                    self.results["false_positives"][predicted_exercise] += 1
            else:
                # Record false negative
                self.results["false_negatives"][exercise_name] += 1
        
        accuracy = (correct_detections / num_iterations) * 100 if num_iterations > 0 else 0
        avg_confidence = np.mean(confidences) if confidences else 0
        avg_latency = np.mean(latencies) if latencies else 0
        
        return {
            "detected": correct_detections > 0,
            "accuracy": accuracy,
            "correct_detections": correct_detections,
            "total_tests": num_iterations,
            "avg_confidence": avg_confidence,
            "avg_latency": avg_latency,
            "status": "PASS" if accuracy >= 80 else "PARTIAL" if accuracy > 0 else "FAIL"
        }
    
    def test_false_positive_rate(self):
        """Test false positives - how often wrong exercises are detected"""
        from types import SimpleNamespace
        
        # Test random poses to see if they trigger incorrect detections
        false_positive_count = 0
        num_random_tests = 100
        
        print("\nTesting False Positive Rate (Random Poses)...")
        print("-" * 60)
        
        for i in range(num_random_tests):
            # Create random landmarks with proper MediaPipe format
            landmarks = []
            for j in range(33):
                lm = SimpleNamespace(
                    x=float(np.random.rand()),
                    y=float(np.random.rand()),
                    z=float(np.random.rand()),
                    visibility=1.0
                )
                landmarks.append(lm)
            
            if self.engine.ml_predictor and self.engine.ml_predictor.is_ready():
                predicted_exercise, confidence = self.engine.ml_predictor.predict(
                    landmarks,
                    confidence_threshold=0.5  # Use threshold for this test
                )
                
                if predicted_exercise:
                    false_positive_count += 1
        
        false_positive_rate = (false_positive_count / num_random_tests) * 100
        return false_positive_rate
    
    def test_multi_view_consistency(self, exercise_name, num_views=5):
        """Test detection consistency across multiple views/angles"""
        from types import SimpleNamespace
        
        if not self.engine.ml_predictor or not self.engine.ml_predictor.is_ready():
            return {"consistent": False, "consistency_score": 0}
        
        detections = []
        
        for view in range(num_views):
            # Create landmarks
            landmarks_array = self.create_mock_landmarks(exercise_name)
            
            # Convert from SimpleNamespace back to array for noise addition
            lm_array = np.array([[lm.x, lm.y, lm.z] for lm in landmarks_array])
            
            # Add slight noise/rotation to simulate different viewing angles
            noise = np.random.normal(0, 0.02, lm_array.shape)
            lm_array = np.clip(lm_array + noise, 0, 1)
            
            # Convert back to SimpleNamespace format
            landmarks = []
            for i in range(33):
                lm = SimpleNamespace(
                    x=float(lm_array[i, 0]),
                    y=float(lm_array[i, 1]),
                    z=float(lm_array[i, 2]),
                    visibility=1.0
                )
                landmarks.append(lm)
            
            predicted_exercise, confidence = self.engine.ml_predictor.predict(
                landmarks,
                confidence_threshold=0.0
            )
            
            if predicted_exercise:
                detections.append(predicted_exercise.lower() == exercise_name.lower())
        
        consistency_score = (sum(detections) / len(detections) * 100) if detections else 0
        
        return {
            "consistent": consistency_score >= 80,
            "consistency_score": consistency_score,
            "successful_views": sum(detections),
            "total_views": num_views
        }
    
    def run_comprehensive_test(self):
        """Run comprehensive detection accuracy test for all 28 exercises"""
        
        print("=" * 80)
        print("COMPREHENSIVE EXERCISE DETECTION ACCURACY TEST")
        print("=" * 80)
        print(f"\nTesting ML Model Detection Accuracy for All 28 Exercises")
        print(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check if ML model is available
        if not self.engine.ml_predictor:
            print("[ERROR] ML predictor not initialized")
            return
        
        if not self.engine.ml_predictor.is_ready():
            print("[ERROR] ML model failed to load")
            print(f"Model path: {self.engine.ml_predictor.model_path}")
            return
        
        print(f"[SUCCESS] ML model loaded: {self.engine.ml_predictor.model_path}")
        print()
        
        # Test by category
        categories = {
            "Shoulder": ALL_EXERCISES[0:6],
            "Elbow": ALL_EXERCISES[6:8],
            "Knee": ALL_EXERCISES[8:10],
            "Hip": ALL_EXERCISES[10:12],
            "Neck": ALL_EXERCISES[12:15],
            "Wrist": ALL_EXERCISES[15:17],
            "Ankle": ALL_EXERCISES[17:22],
            "Squat": ALL_EXERCISES[22:27],
            "Back": ALL_EXERCISES[27:28],
        }
        
        overall_results = {
            "passed": 0,
            "partial": 0,
            "failed": 0,
            "total": 0
        }
        
        category_results = {}
        
        for category, exercises in categories.items():
            print(f"\n{category} Exercises ({len(exercises)})")
            print("-" * 80)
            
            category_passed = 0
            
            for exercise in exercises:
                result = self.test_exercise_detection(exercise, num_iterations=10)
                
                # Test multi-view consistency
                consistency = self.test_multi_view_consistency(exercise, num_views=5)
                
                status_marker = "[PASS]" if result["status"] == "PASS" else "[PART]" if result["status"] == "PARTIAL" else "[FAIL]"
                
                print(f"  {status_marker} {exercise:35} {result['status']:8} "
                      f"({result['accuracy']:5.1f}%) | "
                      f"Conf: {result['avg_confidence']:5.2f} | "
                      f"View: {consistency['consistency_score']:5.1f}%")
                
                self.results["detection_accuracy"][exercise] = result
                
                if result["status"] == "PASS":
                    category_passed += 1
                    overall_results["passed"] += 1
                elif result["status"] == "PARTIAL":
                    overall_results["partial"] += 1
                else:
                    overall_results["failed"] += 1
                
                overall_results["total"] += 1
            
            category_results[category] = {
                "passed": category_passed,
                "total": len(exercises)
            }
            
            print(f"  Category Result: {category_passed}/{len(exercises)} exercises detected successfully")
        
        # Test false positive rate
        print(f"\n{'Robustness & Reliability':^80}")
        print("-" * 80)
        
        false_positive_rate = self.test_false_positive_rate()
        print(f"  False Positive Rate (Random Poses): {false_positive_rate:.1f}%")
        print(f"    -> Lower is better (target: < 5%)")
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"DETECTION ACCURACY SUMMARY")
        print(f"{'='*80}")
        
        print(f"\nOverall Results:")
        print(f"  [PASS] Fully Detected:  {overall_results['passed']:2}/{overall_results['total']} ({overall_results['passed']/overall_results['total']*100:5.1f}%)")
        print(f"  [PART] Partial Detect:  {overall_results['partial']:2}/{overall_results['total']} ({overall_results['partial']/overall_results['total']*100:5.1f}%)")
        print(f"  [FAIL] Not Detected:    {overall_results['failed']:2}/{overall_results['total']} ({overall_results['failed']/overall_results['total']*100:5.1f}%)")
        
        print(f"\nBy Category:")
        for category, result in category_results.items():
            percentage = (result["passed"] / result["total"] * 100) if result["total"] > 0 else 0
            status = "[PASS]" if result["passed"] == result["total"] else "[PART]" if result["passed"] > 0 else "[FAIL]"
            print(f"  {status} {category:15} {result['passed']:1}/{result['total']:1} ({percentage:5.1f}%)")
        
        print(f"\n{'='*80}")
        
        # Determine overall status
        success_rate = overall_results['passed'] / overall_results['total'] * 100
        
        if success_rate >= 90:
            overall_status = "[PASS] EXCELLENT - Production Ready"
        elif success_rate >= 80:
            overall_status = "[PASS] GOOD - Minor improvements needed"
        elif success_rate >= 70:
            overall_status = "[PART] FAIR - Needs refinement"
        else:
            overall_status = "[FAIL] POOR - Requires significant work"
        
        print(f"\nOverall Detection Accuracy: {success_rate:.1f}%")
        print(f"Status: {overall_status}")
        print(f"{'='*80}\n")
        
        return {
            "overall_accuracy": success_rate,
            "passed": overall_results['passed'],
            "partial": overall_results['partial'],
            "failed": overall_results['failed'],
            "false_positive_rate": false_positive_rate
        }


def main():
    """Run the detection accuracy test"""
    
    tester = ExerciseDetectionTester()
    results = tester.run_comprehensive_test()
    
    # Print detailed results for any failures
    if results['failed'] > 0 or results['partial'] > 0:
        print("\n[INFO] Exercises needing attention:")
        for exercise, accuracy_data in tester.results["detection_accuracy"].items():
            if accuracy_data["status"] != "PASS":
                print(f"  - {exercise}: {accuracy_data['status']} "
                      f"({accuracy_data['accuracy']:.1f}% accuracy)")


if __name__ == "__main__":
    main()
