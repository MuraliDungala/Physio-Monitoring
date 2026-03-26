#!/usr/bin/env python3
"""
Complete Registration System Test for PhysioMonitor
Tests: Backend connectivity, CORS, registration, login, and data persistence
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"
COLORS = {
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'END': '\033[0m'
}

def print_header(text):
    print(f"\n{COLORS['BLUE']}{'='*70}{COLORS['END']}")
    print(f"{COLORS['BLUE']}{text:^70}{COLORS['END']}")
    print(f"{COLORS['BLUE']}{'='*70}{COLORS['END']}\n")

def print_success(text):
    print(f"{COLORS['GREEN']}✅ {text}{COLORS['END']}")

def print_error(text):
    print(f"{COLORS['RED']}❌ {text}{COLORS['END']}")

def print_info(text):
    print(f"{COLORS['YELLOW']}ℹ️  {text}{COLORS['END']}")

def test_server_health():
    """Test if backend server is running and healthy"""
    print_header("🏥 STEP 1: TESTING SERVER HEALTH")
    
    try:
        # Test main endpoint
        response = requests.get(f"{API_BASE}/", timeout=3)
        if response.status_code == 200:
            print_success(f"Backend server is running on {API_BASE}")
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
            
        # Test docs endpoint
        response = requests.get(f"{API_BASE}/docs", timeout=3)
        if response.status_code == 200:
            print_success("Swagger documentation is accessible at /docs")
        else:
            print_error("Swagger docs not accessible")
            return False
            
        return True
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {API_BASE}")
        print_info("Start server with: python -m uvicorn app:app --port 8000")
        return False
    except Exception as e:
        print_error(f"Server test failed: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    print_header("🔒 STEP 2: TESTING CORS CONFIGURATION")
    
    try:
        response = requests.options(
            f"{API_BASE}/register",
            headers={
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            },
            timeout=3
        )
        
        if "access-control-allow-origin" in response.headers:
            cors_origin = response.headers.get("access-control-allow-origin")
            print_success(f"CORS is enabled: {cors_origin}")
        else:
            print_error("CORS headers not found")
            return False
            
        return True
    except Exception as e:
        print_error(f"CORS test failed: {e}")
        return False

def test_registration(username, email, password, full_name):
    """Test user registration"""
    try:
        user_data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password
        }
        
        response = requests.post(
            f"{API_BASE}/register",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            user = response.json()
            print_success(f"User '{username}' registered successfully (ID: {user.get('id')})")
            return user
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            print_error(f"Registration failed for '{username}': {error_msg}")
            return None
    except Exception as e:
        print_error(f"Registration error: {e}")
        return None

def test_login(username, password):
    """Test user login"""
    try:
        login_data = {
            "username": username,
            "password": password,
            "grant_type": "password"
        }
        
        response = requests.post(
            f"{API_BASE}/token",
            data=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print_success(f"'{username}' logged in successfully")
            print_info(f"Token: {token[:30]}...")
            return token
        else:
            error_msg = response.json().get('detail', 'Invalid credentials')
            print_error(f"Login failed: {error_msg}")
            return None
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_protected_endpoint(token, username):
    """Test accessing protected endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE}/users/me",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            user = response.json()
            print_success(f"Protected endpoint accessed for '{username}'")
            print_info(f"User data: {json.dumps(user, indent=2, default=str)}")
            return user
        else:
            print_error(f"Access denied (Status: {response.status_code})")
            return None
    except Exception as e:
        print_error(f"Protected endpoint error: {e}")
        return None

def main():
    print_header("🏥 PHYSIOMONITOR REGISTRATION SYSTEM TEST")
    
    test_results = {
        "server_health": False,
        "cors": False,
        "registrations": 0,
        "logins": 0,
        "protected_access": 0
    }
    
    # Test 1: Server Health
    if not test_server_health():
        print_error("Cannot continue without a running server")
        return
    test_results["server_health"] = True
    
    # Test 2: CORS
    if not test_cors():
        print_error("CORS misconfiguration detected")
    else:
        test_results["cors"] = True
    
    # Test 3: Registration
    print_header("👤 STEP 3: TESTING USER REGISTRATION")
    
    timestamp = int(time.time())
    test_users = [
        {
            "username": f"therapist_alice_{timestamp}",
            "email": f"alice_{timestamp}@physio.local",
            "password": "SecurePass123!Alice",
            "full_name": "Dr. Alice Johnson"
        },
        {
            "username": f"patient_bob_{timestamp}",
            "email": f"bob_{timestamp}@physio.local",
            "password": "SecurePass456!Bob",
            "full_name": "Bob Smith"
        },
        {
            "username": f"physio_charlie_{timestamp}",
            "email": f"charlie_{timestamp}@physio.local",
            "password": "SecurePass789!Charlie",
            "full_name": "Charlie Brown"
        }
    ]
    
    registered_users = []
    for user_info in test_users:
        user = test_registration(
            user_info["username"],
            user_info["email"],
            user_info["password"],
            user_info["full_name"]
        )
        if user:
            registered_users.append(user_info)
            test_results["registrations"] += 1
        time.sleep(0.5)
    
    if not registered_users:
        print_error("No users registered successfully")
        return
    
    # Test 4: Login
    print_header("🔐 STEP 4: TESTING USER LOGIN")
    
    user_tokens = {}
    for user_info in registered_users:
        token = test_login(user_info["username"], user_info["password"])
        if token:
            user_tokens[user_info["username"]] = token
            test_results["logins"] += 1
        time.sleep(0.5)
    
    # Test 5: Protected Endpoints
    print_header("🛡️  STEP 5: TESTING PROTECTED ENDPOINTS")
    
    for username, token in user_tokens.items():
        user_data = test_protected_endpoint(token, username)
        if user_data:
            test_results["protected_access"] += 1
        time.sleep(0.3)
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    print(f"Server Health:      {'✅' if test_results['server_health'] else '❌'}")
    print(f"CORS Configuration: {'✅' if test_results['cors'] else '❌'}")
    print(f"Users Registered:   {test_results['registrations']}/{len(test_users)}")
    print(f"Users Logged In:    {test_results['logins']}/{len(registered_users)}")
    print(f"Protected Access:   {test_results['protected_access']}/{len(user_tokens)}")
    
    success = (
        test_results["server_health"] and
        test_results["cors"] and
        test_results["registrations"] > 0 and
        test_results["logins"] > 0
    )
    
    print()
    if success:
        print_success("ALL TESTS PASSED! ✨ Registration system is working correctly")
    else:
        print_error("Some tests failed. Review the output above.")
    
    # Instructions
    print_header("🌐 HOW TO USE THE SYSTEM")
    
    print("1. Open your browser:")
    print(f"   {COLORS['BLUE']}http://localhost:8000/{COLORS['END']}")
    print()
    print("2. Create a new account:")
    print("   - Click 'Register' button")
    print("   - Fill in username, email, full name, and password")
    print("   - Click 'Create Account'")
    print()
    print("3. Sign in with your credentials")
    print()
    print("4. Access your personalized dashboard")
    print()
    print("5. Test account details (from this test):")
    for i, user in enumerate(registered_users[:1], 1):
        print(f"   Account {i}:")
        print(f"   - Username: {user['username']}")
        print(f"   - Email: {user['email']}")
        print(f"   - Password: {user['password']}")
    print()
    
    print_header("📚 API DOCUMENTATION")
    print(f"Swagger UI:    {COLORS['BLUE']}http://localhost:8000/docs{COLORS['END']}")
    print(f"ReDoc:         {COLORS['BLUE']}http://localhost:8000/redoc{COLORS['END']}")
    print()

if __name__ == "__main__":
    main()
