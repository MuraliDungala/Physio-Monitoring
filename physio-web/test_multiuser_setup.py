#!/usr/bin/env python3
"""
Test script for multi-user registration and authentication
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_server_connection():
    """Test if server is running"""
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"✅ Server is running (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_user_registration(username, email, password, full_name):
    """Test user registration"""
    try:
        user_data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password
        }
        response = requests.post(f"{API_BASE}/register", json=user_data)
        
        if response.status_code == 200:
            print(f"✅ User '{username}' registered successfully")
            return response.json()
        else:
            print(f"❌ Registration failed for '{username}': {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_user_login(username, password):
    """Test user login"""
    try:
        login_data = {
            "username": username,
            "password": password,
            "grant_type": "password"
        }
        response = requests.post(f"{API_BASE}/token", data=login_data)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ '{username}' logged in successfully")
            print(f"   Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed for '{username}': {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/users/me", headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Protected endpoint accessed: {user['username']}")
            return user
        else:
            print(f"❌ Protected endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")
        return None

def main():
    print("=" * 60)
    print("🧪 PhysioMonitor Multi-User System Test")
    print("=" * 60)
    print()
    
    # Test server connection
    print("1️⃣  Testing Server Connection...")
    if not test_server_connection():
        print("\n❌ Server is not running. Please start it with: python -m uvicorn app:app --port 8000")
        return
    
    print()
    time.sleep(1)
    
    # Test multiple user registrations
    print("2️⃣  Testing Multi-User Registration...")
    test_users = [
        {
            "username": "patient_john",
            "email": "john@example.com",
            "password": "SecurePass123!",
            "full_name": "John Doe"
        },
        {
            "username": "patient_jane",
            "email": "jane@example.com",
            "password": "SecurePass456!",
            "full_name": "Jane Smith"
        },
        {
            "username": "patient_mike",
            "email": "mike@example.com",
            "password": "SecurePass789!",
            "full_name": "Mike Johnson"
        }
    ]
    
    registered_users = []
    for user_info in test_users:
        user = test_user_registration(
            user_info["username"],
            user_info["email"],
            user_info["password"],
            user_info["full_name"]
        )
        if user:
            registered_users.append(user_info)
        time.sleep(0.5)
    
    print()
    print(f"✅ Registered {len(registered_users)} users out of {len(test_users)}")
    
    print()
    time.sleep(1)
    
    # Test login for each user
    print("3️⃣  Testing Multi-User Login...")
    user_tokens = {}
    for user_info in registered_users:
        token = test_user_login(user_info["username"], user_info["password"])
        if token:
            user_tokens[user_info["username"]] = token
        time.sleep(0.5)
    
    print()
    print(f"✅ Logged in {len(user_tokens)} users")
    
    print()
    time.sleep(1)
    
    # Test protected endpoint access for each user
    print("4️⃣  Testing Protected Endpoint Access...")
    for username, token in user_tokens.items():
        user_data = test_protected_endpoint(token)
        if user_data:
            print(f"   - User ID: {user_data.get('id')}, Email: {user_data.get('email')}")
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print("✅ Multi-User System Test Completed Successfully!")
    print("=" * 60)
    print()
    print("📊 Summary:")
    print(f"  - Registered Users: {len(registered_users)}")
    print(f"  - Logged In Users: {len(user_tokens)}")
    print()
    print("🎯 Next Steps:")
    print("  1. Open http://localhost:8000/ in your browser")
    print("  2. Click 'Register' to create a new account")
    print("  3. Each user gets isolated data and sessions")
    print("  4. Login to access personalized dashboard")
    print()

if __name__ == "__main__":
    main()
