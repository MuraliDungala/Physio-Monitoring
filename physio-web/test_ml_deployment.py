"""
Integration Test: ML Models with Web Backend
=============================================

Tests that all trained models are properly integrated into the web backend
and ready for production use.
"""

import sys
from pathlib import Path
import numpy as np

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from ml_models.advanced_classifier import advanced_classifier
from ml_models.inference_service import ml_service


def test_classifier_loading():
    """Test 1: Verify all models are loaded"""
    print("\n" + "=" * 80)
    print("[TEST 1] MODEL LOADING")
    print("=" * 80)
    
    if not advanced_classifier.is_ready:
        print("❌ FAIL: Classifier not ready")
        return False
    
    print(f"✅ PASS: Classifier ready")
    print(f"   Models: {list(advanced_classifier.models.keys())}")
    
    info = advanced_classifier.get_model_info()
    print(f"   Classes: {info['num_classes']}")
    print(f"   Features required: {info['num_features']}")
    
    return True


def test_basic_prediction():
    """Test 2: Make basic prediction"""
    print("\n" + "=" * 80)
    print("[TEST 2] BASIC PREDICTION")
    print("=" * 80)
    
    features = np.random.randn(132)
    result = advanced_classifier.predict(features)
    
    required_keys = ['exercise', 'confidence', 'method', 'details']
    if not all(k in result for k in required_keys):
        print("❌ FAIL: Missing required keys in result")
        return False
    
    print(f"✅ PASS: Prediction successful")
    print(f"   Exercise: {result['exercise']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Method: {result['method']}")
    
    return True


def test_biomechanics_fallback():
    """Test 3: Test biomechanics fallback logic"""
    print("\n" + "=" * 80)
    print("[TEST 3] BIOMECHANICS FALLBACK")
    print("=" * 80)
    
    features = np.random.randn(132)
    
    biomech_info = {
        'exercise': 'Hip Abduction',
        'confidence': 0.95,
        'quality_score': 85,
        'posture_valid': True,
        'reps_count': 3
    }
    
    result = advanced_classifier.predict(features, biomech_info)
    
    if result['method'] not in ['ML_HIGH_CONFIDENCE', 'BIOMECHANICS_FALLBACK', 'ML_LOW_CONFIDENCE']:
        print(f"❌ FAIL: Invalid method: {result['method']}")
        return False
    
    print(f"✅ PASS: Fallback logic working")
    print(f"   Decision method: {result['method']}")
    print(f"   Final exercise: {result['exercise']}")
    print(f"   Biomechanics fallback available: {result.get('biomechanics_prediction', 'N/A')}")
    
    return True


def test_threshold_adjustment():
    """Test 4: Test confidence threshold adjustment"""
    print("\n" + "=" * 80)
    print("[TEST 4] THRESHOLD ADJUSTMENT")
    print("=" * 80)
    
    try:
        original = advanced_classifier.confidence_threshold
        
        # Test adjustment
        advanced_classifier.set_confidence_threshold(0.85)
        if advanced_classifier.confidence_threshold != 0.85:
            print("❌ FAIL: Threshold not adjusted")
            return False
        
        # Test invalid threshold
        try:
            advanced_classifier.set_confidence_threshold(1.5)
            print("❌ FAIL: Should reject invalid threshold")
            return False
        except ValueError:
            pass  # Expected
        
        # Reset
        advanced_classifier.set_confidence_threshold(original)
        
        print(f"✅ PASS: Threshold adjustment working")
        print(f"   Original: {original:.2f}")
        print(f"   Adjusted: 0.85")
        print(f"   Reset: {advanced_classifier.confidence_threshold:.2f}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_inference_service():
    """Test 5: Test inference service wrapper"""
    print("\n" + "=" * 80)
    print("[TEST 5] INFERENCE SERVICE")
    print("=" * 80)
    
    try:
        features = np.random.randn(132)
        result = ml_service.classify_exercise(
            features=features,
            user_id='test_user'
        )
        
        if result.get('method') == 'ERROR':
            print(f"❌ FAIL: Service error: {result.get('error')}")
            return False
        
        print(f"✅ PASS: Inference service working")
        print(f"   Exercise: {result['exercise']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Request ID: {result.get('request_id')}")
        
        # Check service info
        info = ml_service.get_classifier_info()
        print(f"   Total requests: {info['total_requests']}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_batch_processing():
    """Test 6: Test batch inference"""
    print("\n" + "=" * 80)
    print("[TEST 6] BATCH PROCESSING")
    print("=" * 80)
    
    try:
        features_list = [np.random.randn(132) for _ in range(3)]
        results = ml_service.batch_classify(features_list)
        
        if len(results) != 3:
            print(f"❌ FAIL: Expected 3 results, got {len(results)}")
            return False
        
        print(f"✅ PASS: Batch processing working")
        for i, result in enumerate(results):
            print(f"   Sample {i+1}: {result['exercise']} ({result['confidence']:.2f})")
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_production_readiness():
    """Test 7: Overall production readiness"""
    print("\n" + "=" * 80)
    print("[TEST 7] PRODUCTION READINESS")
    print("=" * 80)
    
    checks = {
        "Classifier ready": advanced_classifier.is_ready,
        "Models loaded": len(advanced_classifier.models) == 3,
        "Inference service ready": ml_service.classifier.is_ready,
        "Confidence threshold valid": 0.0 <= advanced_classifier.confidence_threshold <= 1.0,
    }
    
    all_passed = all(checks.values())
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    if all_passed:
        print(f"\n✅ PASS: All production checks passed")
    else:
        print(f"\n❌ FAIL: Some checks failed")
    
    return all_passed


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 80)
    print("PHYSIO-MONITORING WEB BACKEND - ML DEPLOYMENT TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Model Loading", test_classifier_loading),
        ("Basic Prediction", test_basic_prediction),
        ("Biomechanics Fallback", test_biomechanics_fallback),
        ("Threshold Adjustment", test_threshold_adjustment),
        ("Inference Service", test_inference_service),
        ("Batch Processing", test_batch_processing),
        ("Production Readiness", test_production_readiness),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'=' * 80}")
    print(f"RESULT: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'=' * 80}\n")
    
    if passed == total:
        print("🚀 WEB BACKEND DEPLOYMENT SUCCESSFUL - READY FOR PRODUCTION")
    else:
        print("⚠️  Some tests failed - review errors above")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
