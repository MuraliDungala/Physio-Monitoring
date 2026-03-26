"""
Test Frontend API Calls - Mimics browser behavior
"""

import requests
import json

print("\n" + "=" * 80)
print("FRONTEND API DETAILED TEST")
print("=" * 80 + "\n")

# Test with proper headers like browser would send
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'http://localhost:3000'
}

BASE_URL = "http://127.0.0.1:8000"

# Test 1: Simple GET request
print("[TEST 1] Basic GET /exercises")
try:
    response = requests.get(f"{BASE_URL}/exercises", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Loaded {len(data)} exercises")
        print(f"First exercise: {data[0] if data else 'None'}")
    else:
        print(f"❌ Error response:")
        print(f"   Text: {response.text[:500]}")
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")

# Test 2: Get category exercises
print("\n[TEST 2] GET /exercises/category/Shoulder")
try:
    response = requests.get(
        f"{BASE_URL}/exercises/category/Shoulder",
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Loaded {len(data)} shoulder exercises")
        for ex in data:
            print(f"   • {ex.get('name', 'Unknown')}")
    else:
        print(f"❌ Error status {response.status_code}")
        print(f"   Text: {response.text[:500]}")
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")

# Test 3: Get categories
print("\n[TEST 3] GET /exercises/categories")
try:
    response = requests.get(
        f"{BASE_URL}/exercises/categories",
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response type: {type(response.json())}")
    print(f"Response content: {response.json()}")
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"✅ Success! Got {len(data)} categories")
            for cat in data:
                print(f"   • {cat}")
        else:
            print(f"⚠️  Unexpected format (not a list):")
            print(f"   {data}")
    else:
        print(f"❌ Error status {response.status_code}")
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")

# Test 4: OPTIONS request (CORS preflight)
print("\n[TEST 4] OPTIONS /exercises/category/Shoulder (CORS Preflight)")
try:
    response = requests.options(
        f"{BASE_URL}/exercises/category/Shoulder",
        headers={
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'content-type'
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"CORS Headers:")
    for key, value in response.headers.items():
        if 'Access-Control' in key or 'Allow' in key:
            print(f"   {key}: {value}")
    if response.status_code in [200, 204]:
        print(f"✅ CORS preflight successful")
    else:
        print(f"⚠️  Unexpected status for OPTIONS: {response.status_code}")
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")

# Test 5: Test connection to backend
print("\n[TEST 5] Backend Health Check")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    print(f"✅ Backend is reachable (status {response.status_code})")
except requests.exceptions.ConnectionError:
    print(f"❌ Cannot connect to backend at {BASE_URL}")
    print(f"   Make sure the backend is running on port 8000")
    print(f"   Run: cd physio-web/backend && uvicorn app:app --reload")
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80 + "\n")

print("""
COMMON CAUSES OF "FAILED TO LOAD EXERCISES":
============================================

1. CORS Error (Most Common)
   - Browser blocks cross-origin request
   - Check browser console for "CORS policy" error
   - Solution: Verify CORS is configured in backend
   
2. Backend Not Running
   - Port 8000 not listening
   - Solution: Start backend with: uvicorn app:app --reload
   
3. Wrong Port/Hostname
   - Frontend trying wrong URL
   - Solution: Check API_BASE in script.js
   
4. API Endpoint Error
   - Backend returns error status (500, 404, etc.)
   - Solution: Check backend logs for error messages
   
5. Network Timeout
   - Backend taking too long to respond
   - Solution: Check backend is not stuck/frozen

HOW TO DEBUG IN BROWSER:
======================
1. Open F12 (Developer Tools)
2. Go to Network tab
3. Click exercise category
4. Look for the failing request
5. Click it to see:
   - Status code
   - Response headers
   - Error response text

NEXT STEPS:
===========
1. Check browser console (F12 → Console)
2. Look for error message details
3. Run this test (output above)
4. Compare results with expected behavior
""")
