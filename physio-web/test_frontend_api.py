"""
Frontend API Connectivity and Exercise Loading Test
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("\n" + "=" * 80)
print("FRONTEND API CONNECTIVITY TEST")
print("=" * 80 + "\n")

# Test 1: Get all exercises
print("[TEST 1] GET /exercises")
try:
    response = requests.get(f"{BASE_URL}/exercises")
    if response.status_code == 200:
        exercises = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   Total exercises: {len(exercises)}")
        if exercises:
            print(f"   Sample: {exercises[0]['name']}")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 2: Get exercises by category
print("\n[TEST 2] GET /exercises/category/Shoulder")
try:
    response = requests.get(f"{BASE_URL}/exercises/category/Shoulder")
    if response.status_code == 200:
        exercises = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   Shoulder exercises: {len(exercises)}")
        for ex in exercises:
            print(f"      • {ex['name']}")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 3: Get all categories
print("\n[TEST 3] GET /exercises/categories")
try:
    response = requests.get(f"{BASE_URL}/exercises/categories")
    if response.status_code == 200:
        categories = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   Available categories: {len(categories)}")
        for cat in sorted(categories):
            print(f"      • {cat}")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 80)
print("FRONTEND API CONNECTIVITY TEST COMPLETE")
print("=" * 80 + "\n")
