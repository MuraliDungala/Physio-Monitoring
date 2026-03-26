import requests
import json

url = "http://127.0.0.1:8001/exercises"
print(f"Testing API endpoint: {url}")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"✓ Exercises returned: {len(data)}")
            print(f"First exercise: {data[0]['name'] if data else 'None'}")
        else:
            print(f"Response type: {type(data)}")
            print(f"Response: {json.dumps(data, indent=2)[:200]}")
    else:
        print(f"Error response: {response.text[:200]}")
except Exception as e:
    print(f"Connection error: {e}")
