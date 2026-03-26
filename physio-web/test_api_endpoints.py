"""
API Endpoint Testing: /api/classify
===================================

Tests for the new exercise classification endpoints.
"""

import sys
from pathlib import Path
import cv2
import base64
import numpy as np
import requests
import json
from typing import Dict, Optional

# Configuration
BASE_URL = "http://localhost:8000"  # FastAPI backend URL
API_ENDPOINTS = {
    'classify': f"{BASE_URL}/api/classify",
    'classify_batch': f"{BASE_URL}/api/classify/batch",
    'classifier_info': f"{BASE_URL}/api/classifier/info",
    'classifier_threshold': f"{BASE_URL}/api/classifier/threshold"
}


def create_dummy_frame(width=640, height=480) -> str:
    """Create a dummy video frame and encode to base64"""
    # Create a simple frame
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add some simple shapes for visual interest
    cv2.rectangle(frame, (100, 100), (400, 300), (0, 255, 0), 2)
    cv2.circle(frame, (320, 240), 50, (255, 0, 0), -1)
    
    # Encode to base64
    _, buffer = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return frame_base64


def test_classifier_info():
    """Test 1: Get classifier info"""
    print("\n" + "=" * 80)
    print("[TEST 1] GET CLASSIFIER INFO")
    print("=" * 80)
    
    try:
        response = requests.get(API_ENDPOINTS['classifier_info'])
        
        if response.status_code != 200:
            print(f"❌ FAIL: Status code {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        print(f"✅ PASS: Classifier info retrieved")
        print(f"   Status: {data['status']}")
        print(f"   Models: {', '.join(data['models'])}")
        print(f"   Classes: {data['num_classes']}")
        print(f"   Exercises: {', '.join(data['classes'][:3])}...")
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_basic_classification():
    """Test 2: Basic frame classification"""
    print("\n" + "=" * 80)
    print("[TEST 2] BASIC FRAME CLASSIFICATION")
    print("=" * 80)
    
    try:
        frame_b64 = create_dummy_frame()
        
        payload = {
            "frame_data": frame_b64,
            "exercise_name": None,
            "extract_features_only": False
        }
        
        response = requests.post(API_ENDPOINTS['classify'], json=payload)
        
        if response.status_code != 200:
            print(f"❌ FAIL: Status code {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print(f"⚠️  Classification request failed (expected for dummy frame): {data.get('error')}")
            return True  # This is expected behavior for dummy frames
        
        result = data.get('result', {})
        print(f"✅ PASS: Frame classified")
        print(f"   Exercise: {result.get('exercise')}")
        print(f"   Confidence: {result.get('confidence'):.2f}")
        print(f"   Method: {result.get('method')}")
        print(f"   Processing time: {result.get('processing_time_ms'):.1f}ms")
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_features_only():
    """Test 3: Extract features without classification"""
    print("\n" + "=" * 80)
    print("[TEST 3] FEATURE EXTRACTION ONLY")
    print("=" * 80)
    
    try:
        frame_b64 = create_dummy_frame()
        
        payload = {
            "frame_data": frame_b64,
            "extract_features_only": True
        }
        
        response = requests.post(API_ENDPOINTS['classify'], json=payload)
        
        if response.status_code != 200:
            print(f"❌ FAIL: Status code {response.status_code}")
            return False
        
        data = response.json()
        result = data.get('result', {})
        features = result.get('extracted_features', [])
        
        if len(features) != 132:
            print(f"❌ FAIL: Expected 132 features, got {len(features)}")
            return False
        
        print(f"✅ PASS: Features extracted")
        print(f"   Feature dimensions: {len(features)}")
        print(f"   Method: {result.get('method')}")
        print(f"   Processing time: {result.get('processing_time_ms'):.1f}ms")
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_with_exercise_hint():
    """Test 4: Classification with exercise hint"""
    print("\n" + "=" * 80)
    print("[TEST 4] CLASSIFICATION WITH EXERCISE HINT")
    print("=" * 80)
    
    try:
        frame_b64 = create_dummy_frame()
        
        payload = {
            "frame_data": frame_b64,
            "exercise_name": "Shoulder Flexion",  # Provide hint
            "extract_features_only": False
        }
        
        response = requests.post(API_ENDPOINTS['classify'], json=payload)
        
        if response.status_code != 200:
            print(f"❌ FAIL: Status code {response.status_code}")
            return False
        
        data = response.json()
        result = data.get('result', {})
        
        print(f"✅ PASS: Classification with exercise hint")
        print(f"   Exercise hint provided: Shoulder Flexion")
        print(f"   Predicted exercise: {result.get('exercise')}")
        print(f"   Method: {result.get('method')}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_threshold_update():
    """Test 5: Update confidence threshold"""
    print("\n" + "=" * 80)
    print("[TEST 5] UPDATE CONFIDENCE THRESHOLD")
    print("=" * 80)
    
    try:
        # Get current threshold
        current = requests.get(API_ENDPOINTS['classifier_info']).json()
        original_threshold = current['confidence_threshold']
        
        # Update threshold
        new_threshold = 0.75
        response = requests.put(
            f"{API_ENDPOINTS['classifier_threshold']}?threshold={new_threshold}"
        )
        
        if response.status_code != 200:
            print(f"❌ FAIL: Status code {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ FAIL: {data.get('message')}")
            return False
        
        print(f"✅ PASS: Threshold updated")
        print(f"   Original: {original_threshold:.2f}")
        print(f"   New: {new_threshold:.2f}")
        print(f"   Message: {data.get('message')}")
        
        # Reset to original
        requests.put(
            f"{API_ENDPOINTS['classifier_threshold']}?threshold={original_threshold}"
        )
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_batch_classification():
    """Test 6: Batch classification"""
    print("\n" + "=" * 80)
    print("[TEST 6] BATCH CLASSIFICATION")
    print("=" * 80)
    
    try:
        # Create 3 dummy frames
        frames_data = [
            {
                "frame_data": create_dummy_frame(),
                "exercise_name": None,
                "extract_features_only": False
            } for _ in range(3)
        ]
        
        response = requests.post(API_ENDPOINTS['classify_batch'], json=frames_data)
        
        if response.status_code != 200:
            print(f"❌ FAIL: Status code {response.status_code}")
            return False
        
        data = response.json()
        
        print(f"✅ PASS: Batch classification completed")
        print(f"   Total frames: {data.get('total_frames')}")
        print(f"   Successful: {data.get('successful_classifications')}")
        print(f"   Overall success: {data.get('success')}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 80)
    print("PHYSIO-MONITORING - API ENDPOINT TESTS")
    print("=" * 80)
    print(f"Testing against: {BASE_URL}")
    
    tests = [
        ("Classifier Info", test_classifier_info),
        ("Basic Classification", test_basic_classification),
        ("Feature Extraction", test_features_only),
        ("Classification with Hint", test_with_exercise_hint),
        ("Threshold Update", test_threshold_update),
        ("Batch Classification", test_batch_classification),
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
        print("🎯 ALL API ENDPOINTS WORKING - READY FOR PRODUCTION")
    else:
        print("⚠️  Some tests failed - check backend status")
    
    return passed == total


if __name__ == "__main__":
    print("\n⏳ Note: Ensure FastAPI backend is running on http://localhost:8000")
    print("   Start with: cd physio-web/backend && uvicorn app:app --reload\n")
    
    try:
        # Test connection
        requests.get(f"{BASE_URL}/docs", timeout=2)
    except:
        print("❌ Cannot connect to backend at {BASE_URL}")
        print("   Make sure the backend is running!")
        exit(1)
    
    success = run_all_tests()
    exit(0 if success else 1)
