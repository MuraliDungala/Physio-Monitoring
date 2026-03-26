#!/usr/bin/env python3
import requests
import json
import time

url = 'http://127.0.0.1:8000/register'
timestamp = int(time.time())
data = {
    'username': f'testuser_{timestamp}',
    'email': f'test_{timestamp}@example.com',
    'password': 'TestPass123!',
    'full_name': 'Test User'
}

print('='*60)
print('BACKEND /register ENDPOINT TEST')
print('='*60)
print(f'\nURL: {url}')
print(f'Data: {json.dumps(data, indent=2)}')
print('\nSending request...\n')

try:
    response = requests.post(url, json=data, timeout=5)
    
    print(f'Status Code: {response.status_code}')
    print(f'Response Headers: {dict(response.headers)}')
    print(f'Response Body: {response.text}')
    
    if response.status_code == 200:
        print('\nSUCCESS: Registration endpoint is WORKING!')
        print('Backend is responding correctly.')
    else:
        print(f'\nERROR: {response.json()}')
except Exception as e:
    print(f'FAILED: {e}')
    print('Backend is not reachable!')
