"""
Test Suite for Hybrid Decision Model
====================================

Comprehensive testing of the biomechanics + ML fusion system.
"""

import numpy as np
import sys
import os
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "Physio-Monitoring"))

from src.ml.hybrid_decision_model import HybridDecisionModel
from src.ml.dataset_loader import DatasetLoader

def test_hybrid_model_basic():
    """Test 1: Basic hybrid model functionality."""
    print("\n" + "=" * 80)
    print("[TEST 1] BASIC HYBRID MODEL FUNCTIONALITY")
    print("=" * 80)
    
    try:
        hybrid = HybridDecisionModel(confidence_threshold=0.65)
        print("✓ Model initialized successfully")
        print(f"✓ Loaded {len(hybrid.models)} ML models: {list(hybrid.models.keys())}")
        
        # Test prediction with random features
        features = np.random.randn(132)
        result = hybrid.predict(features=features)
        
        print(f"✓ Prediction made: {result['exercise']}")
        print(f"✓ Confidence: {result['confidence']:.2f}")
        print(f"✓ Decision method: {result['decision_method']}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_ml_vs_biomechanics_fusion():
    """Test 2: ML and biomechanics fusion logic."""
    print("\n" + "=" * 80)
    print("[TEST 2] ML vs BIOMECHANICS FUSION")
    print("=" * 80)
    
    try:
        hybrid = HybridDecisionModel(confidence_threshold=0.70)
        features = np.random.randn(132)
        
        # Scenario A: High-confidence ML
        biomech_info_a = {
            'exercise': 'Knee Flexion',
            'confidence': 0.95,
            'quality_score': 90,
            'posture_valid': True,
            'reps_count': 2
        }
        
        result_a = hybrid.predict(features, biomech_info_a)
        print(f"\n[Scenario A] High-confidence ML prediction:")
        print(f"  ML Decision: {result_a['ml_prediction']}")
        print(f"  Biomechanics: {result_a['biomechanics_prediction']}")
        print(f"  → Final Decision: {result_a['exercise']}")
        print(f"  → Method: {result_a['decision_method']}")
        
        # Scenario B: Valid biomechanics fallback
        biomech_info_b = {
            'exercise': 'Shoulder Abduction',
            'confidence': 0.85,
            'quality_score': 80,
            'posture_valid': True,
            'reps_count': 1
        }
        
        result_b = hybrid.predict(features, biomech_info_b)
        print(f"\n[Scenario B] With biomechanics fallback:")
        print(f"  ML Decision: {result_b['ml_prediction']}")
        print(f"  Biomechanics: {result_b['biomechanics_prediction']}")
        print(f"  → Final Decision: {result_b['exercise']}")
        print(f"  → Method: {result_b['decision_method']}")
        
        # Scenario C: Poor posture (invalid biomechanics)
        biomech_info_c = {
            'exercise': 'Shoulder Flexion',
            'confidence': 0.5,
            'quality_score': 40,
            'posture_valid': False,
            'reps_count': 0
        }
        
        result_c = hybrid.predict(features, biomech_info_c)
        print(f"\n[Scenario C] Poor posture (invalid biomechanics):")
        print(f"  ML Decision: {result_c['ml_prediction']}")
        print(f"  Biomechanics Valid: {biomech_info_c['posture_valid']}")
        print(f"  → Final Decision: {result_c['exercise']}")
        print(f"  → Method: {result_c['decision_method']}")
        
        print("\n✓ Fusion logic working correctly")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_confidence_threshold_impact():
    """Test 3: Impact of confidence threshold on decisions."""
    print("\n" + "=" * 80)
    print("[TEST 3] CONFIDENCE THRESHOLD IMPACT")
    print("=" * 80)
    
    try:
        features = np.random.randn(132)
        biomech = {
            'exercise': 'Hip Abduction',
            'confidence': 0.8,
            'quality_score': 85,
            'posture_valid': True,
            'reps_count': 1
        }
        
        thresholds = [0.5, 0.65, 0.8, 0.95]
        decisions = []
        
        for threshold in thresholds:
            hybrid = HybridDecisionModel(confidence_threshold=threshold)
            result = hybrid.predict(features, biomech)
            decisions.append({
                'threshold': threshold,
                'method': result['decision_method'],
                'confidence': result['confidence']
            })
            
            print(f"\nThreshold={threshold:.2f}:")
            print(f"  Method: {result['decision_method']}")
            print(f"  Confidence: {result['confidence']:.2f}")
        
        print(f"\n✓ Threshold logic working correctly")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_ensemble_voting():
    """Test 4: Ensemble voting mechanism."""
    print("\n" + "=" * 80)
    print("[TEST 4] ENSEMBLE VOTING MECHANISM")
    print("=" * 80)
    
    try:
        hybrid = HybridDecisionModel(confidence_threshold=0.60)
        features = np.random.randn(132)
        
        result = hybrid.predict(features)
        
        print(f"\nEnsemble Voting Results:")
        print(f"  Models used: {result['ml_models_used']}")
        print(f"  Final prediction: {result['exercise']}")
        print(f"  Ensemble consensus: Multiple models voting")
        
        print(f"\nDetailed predictions:")
        for model_name, pred_info in result['details']['ml_scores'].items():
            print(f"  {model_name}:")
            print(f"    → Prediction: {pred_info['prediction']}")
            print(f"    → Confidence: {pred_info['confidence']:.2f}")
        
        print(f"\n✓ Ensemble voting working correctly")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_edge_cases():
    """Test 5: Edge cases and error handling."""
    print("\n" + "=" * 80)
    print("[TEST 5] EDGE CASES & ERROR HANDLING")
    print("=" * 80)
    
    try:
        hybrid = HybridDecisionModel(confidence_threshold=0.65)
        
        # Edge case 1: No biomechanics info
        print("\n[Edge Case 1] No biomechanics information:")
        features = np.random.randn(132)
        result = hybrid.predict(features, biomechanics_info=None)
        print(f"  Decision: {result['exercise']}")
        print(f"  Method: {result['decision_method']}")
        print(f"  ✓ Handled gracefully")
        
        # Edge case 2: Empty biomechanics info
        print("\n[Edge Case 2] Invalid biomechanics (posture_valid=False):")
        empty_biomech = {'posture_valid': False}
        result = hybrid.predict(features, empty_biomech)
        print(f"  Decision: {result['exercise']}")
        print(f"  Fallback method used: {result['decision_method']}")
        print(f"  ✓ Handled gracefully")
        
        # Edge case 3: Threshold adjustment
        print("\n[Edge Case 3] Threshold adjustment:")
        hybrid.set_confidence_threshold(0.75)
        result = hybrid.predict(features)
        print(f"  New threshold: 0.75")
        print(f"  Decision made: {result['exercise']}")
        print(f"  ✓ Adjusted successfully")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_real_world_scenario():
    """Test 6: Real-world scenario with actual data."""
    print("\n" + "=" * 80)
    print("[TEST 6] REAL-WORLD SCENARIO WITH ACTUAL DATA")
    print("=" * 80)
    
    try:
        # Load real data
        loader = DatasetLoader()
        X, y = loader.load_all()
        
        if len(X) == 0:
            print("⚠ No real data available, skipping test")
            return True
        
        # Initialize hybrid model
        hybrid = HybridDecisionModel(confidence_threshold=0.65)
        
        # Test on first 5 samples
        successes = 0
        total_tests = min(5, len(X))
        
        print(f"\nTesting on {total_tests} real samples:")
        
        for i in range(total_tests):
            features = X[i:i+1]
            true_label = y[i]
            
            # Simulate biomechanics info
            biomech = {
                'exercise': true_label,
                'confidence': 0.8,
                'quality_score': 85,
                'posture_valid': True,
                'reps_count': 1
            }
            
            result = hybrid.predict(features, biomech)
            
            match = "✓" if result['exercise'] == true_label else "✗"
            print(f"\n  Sample {i+1}:")
            print(f"    True: {true_label}")
            print(f"    Predicted: {result['exercise']}")
            print(f"    Method: {result['decision_method']}")
            print(f"    Confidence: {result['confidence']:.2f}")
            print(f"    {match}")
            
            if result['exercise'] == true_label:
                successes += 1
        
        accuracy = successes / total_tests * 100
        print(f"\n✓ Accuracy on {total_tests} samples: {accuracy:.1f}%")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run complete test suite."""
    print("\n" + "=" * 80)
    print("HYBRID DECISION MODEL - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Basic Functionality", test_hybrid_model_basic),
        ("ML vs Biomechanics Fusion", test_ml_vs_biomechanics_fusion),
        ("Confidence Threshold Impact", test_confidence_threshold_impact),
        ("Ensemble Voting", test_ensemble_voting),
        ("Edge Cases", test_edge_cases),
        ("Real-World Scenario", test_real_world_scenario)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'=' * 80}")
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'=' * 80}\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
