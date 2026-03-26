"""Quick API endpoint tests"""
import requests
import json
import base64
import numpy as np

BASE_URL = "http://127.0.0.1:8000"

print("\n" + "=" * 80)
print("LIVE API ENDPOINT TESTS")
print("=" * 80 + "\n")

# Test 1: Classifier Info
print("[TEST 1] GET /api/classifier/info")
try:
    response = requests.get(f"{BASE_URL}/api/classifier/info")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Models: {data.get('models')}")
        print(f"     Classes: {data.get('num_classes')}")
        print(f"     Status: {data.get('status')}")
    else:
        print(f"  ❌ Error: {response.text[:100]}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 2: Update Threshold
print("\n[TEST 2] PUT /api/classifier/threshold")
try:
    response = requests.put(
        f"{BASE_URL}/api/classifier/threshold",
        json={"threshold": 0.7},
        params={"threshold": 0.7}
    )
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  ✅ Threshold updated")
    else:
        print(f"  ❌ Response: {response.text[:100]}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

# Test 3: Create dummy frame and test classification
print("\n[TEST 3] POST /api/classify (dummy frame)")
try:
    # Create a simple dummy frame (100x100 RGB)
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buffer = __import__('cv2').imencode('.jpg', dummy_frame)
    frame_b64 = base64.b64encode(buffer).decode('utf-8')
    
    request_data = {
        "frame_data": frame_b64,
        "exercise_name": None,
        "extract_features_only": False
    }
    
    response = requests.post(f"{BASE_URL}/api/classify", json=request_data)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Response received")
        print(f"     Success: {data.get('success')}")
        if data.get('result'):
            print(f"     Exercise: {data['result'].get('exercise')}")
            print(f"     Confidence: {data['result'].get('confidence'):.2f}")
    else:
        print(f"  ❌ Status {response.status_code}")
        print(f"     {response.text[:200]}")
except Exception as e:
    print(f"  ❌ Exception: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Batch classification
print("\n[TEST 4] POST /api/classify/batch")
try:
    # Create 2 simple frames
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buffer = __import__('cv2').imencode('.jpg', dummy_frame)
    frame_b64 = base64.b64encode(buffer).decode('utf-8')
    
    # Batch expects a list of ClassifyRequest objects
    request_data = [
        {"frame_data": frame_b64, "exercise_name": None, "extract_features_only": False},
        {"frame_data": frame_b64, "exercise_name": None, "extract_features_only": False}
    ]
    
    response = requests.post(f"{BASE_URL}/api/classify/batch", json=request_data)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Batch processing successful")
        print(f"     Results count: {len(data.get('results', []))}")
        print(f"     Successful: {data.get('successful_classifications')}/{data.get('total_frames')}")
    else:
        print(f"  ❌ Status {response.status_code}")
        print(f"     {response.text[:200]}")
except Exception as e:
    print(f"  ❌ Exception: {e}")

print("\n" + "=" * 80)
print("API TESTS COMPLETE")
print("=" * 80 + "\n")
