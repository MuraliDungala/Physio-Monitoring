import requests
import sys

def check_backend():
    print("Testing Backend Connection...")
    try:
        # Test 1: Health Check
        print("\n1. Health Check (http://localhost:8001/health)")
        resp = requests.get('http://localhost:8001/health')
        print(f"Status: {resp.status_code}")
        print(f"Content: {resp.text}")

        # Test 2: Get Exercises
        print("\n2. Get Exercises (http://localhost:8001/exercises)")
        resp = requests.get('http://localhost:8001/exercises')
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Found {len(data)} exercises")
            if len(data) > 0:
                print(f"First exercise: {data[0]['name']}")
        else:
            print(f"Error content: {resp.text}")

        # Test 3: Check CORS headers (roughly)
        print("\n3. Checking Headers")
        print(f"Access-Control-Allow-Origin: {resp.headers.get('access-control-allow-origin')}")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    check_backend()
