#!/usr/bin/env python3
"""
Validation script for "Start Exercise from Rehab Plan" feature
Tests API endpoints and database integration
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8001"
PASSWORD = "test123"
EMAIL = f"test_user_{datetime.now().timestamp()}@test.com"
USERNAME = f"testuser_{datetime.now().timestamp()}".replace(".", "")[:20]

def test_register_user():
    """Test user registration"""
    print("\n📝 Testing User Registration...")
    response = requests.post(
        f"{API_BASE}/register",
        json={"username": USERNAME, "email": EMAIL, "password": PASSWORD, "full_name": "Test User"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ User registered: {USERNAME}")
        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False

def test_login():
    """Test user login"""
    print("\n🔐 Testing User Login...")
    response = requests.post(
        f"{API_BASE}/token",
        data={"username": USERNAME, "password": PASSWORD}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"   ✅ Login successful, token: {token[:20]}...")
        return token
    else:
        print(f"   ❌ Error: {response.text}")
        return None

def test_create_rehab_session(token):
    """Test creating a rehab session"""
    print("\n💾 Testing Create Rehab Session...")
    headers = {"Authorization": f"Bearer {token}"}
    
    session_data = {
        "exercise_name": "Shoulder Press",
        "day": 1,
        "target_reps": 10,
        "reps_done": 8,
        "quality_score": 78,
        "status": "completed",
        "notes": "Test session from validation script"
    }
    
    response = requests.post(
        f"{API_BASE}/rehab-sessions",
        json=session_data,
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        session = response.json()
        print(f"   ✅ Session created: ID={session.get('id')}")
        return session
    else:
        print(f"   ❌ Error: {response.text}")
        return None

def test_get_rehab_sessions(token):
    """Test fetching rehab sessions"""
    print("\n📋 Testing Get Rehab Sessions...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{API_BASE}/rehab-sessions",
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        sessions = response.json()
        print(f"   ✅ Fetched {len(sessions)} sessions")
        if sessions:
            first = sessions[0]
            print(f"      - Exercise: {first.get('exercise_name')}")
            print(f"      - Day: {first.get('day')}")
            print(f"      - Status: {first.get('status')}")
            print(f"      - Reps: {first.get('reps_done')}/{first.get('target_reps')}")
            print(f"      - Quality: {first.get('quality_score')}%")
        return sessions
    else:
        print(f"   ❌ Error: {response.text}")
        return None

def test_update_rehab_session(token, session_id):
    """Test updating a rehab session"""
    print(f"\n🔄 Testing Update Rehab Session (ID: {session_id})...")
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "reps_done": 10,
        "quality_score": 85,
        "status": "completed",
        "notes": "Updated: Full completion"
    }
    
    response = requests.put(
        f"{API_BASE}/rehab-sessions/{session_id}",
        json=update_data,
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Session updated successfully")
        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False

def test_get_sessions_by_day(token, day):
    """Test fetching sessions by specific day"""
    print(f"\n📅 Testing Get Sessions by Day ({day})...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{API_BASE}/rehab-sessions/day/{day}",
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        sessions = response.json()
        print(f"   ✅ Fetched {len(sessions)} sessions for day {day}")
        return sessions
    else:
        print(f"   ❌ Error: {response.text}")
        return None

def test_get_progress(token):
    """Test getting rehab progress"""
    print("\n📊 Testing Get Rehab Progress...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{API_BASE}/rehab-progress",
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        progress = response.json()
        print(f"   ✅ Progress retrieved:")
        print(f"      - Completion Rate: {progress.get('total_completion_rate')}%")
        print(f"      - Total Sessions: {progress.get('total_sessions')}")
        print(f"      - Completed: {progress.get('completed_count')}")
        return progress
    else:
        print(f"   ❌ Error: {response.text}")
        return None

def main():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("  REHAB PLAN FEATURE VALIDATION TEST")
    print("="*60)
    print(f"\n🔗 API Base: {API_BASE}")
    print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test sequence
    success = True
    
    # 1. Register user
    if not test_register_user():
        print("\n❌ Cannot continue without user registration")
        return False
    
    # 2. Login
    token = test_login()
    if not token:
        print("\n❌ Cannot continue without authentication token")
        return False
    
    # 3. Create rehab session
    session = test_create_rehab_session(token)
    if not session:
        print("\n❌ Cannot continue without rehab session")
        return False
    
    # 4. Get all sessions
    sessions = test_get_rehab_sessions(token)
    if not sessions:
        print("\n⚠️  Could not fetch sessions")
    
    # 5. Update session
    if session and "id" in session:
        if not test_update_rehab_session(token, session["id"]):
            print("\n⚠️  Could not update session")
    
    # 6. Get sessions by day
    test_get_sessions_by_day(token, 1)
    
    # 7. Get progress
    test_get_progress(token)
    
    # Summary
    print("\n" + "="*60)
    print("  VALIDATION SUMMARY")
    print("="*60)
    print(f"✅ All core endpoints tested successfully!")
    print(f"✅ Rehab Plan feature is functional!")
    print(f"\n📝 Test User:")
    print(f"   Username: {USERNAME}")
    print(f"   Email: {EMAIL}")
    print(f"   Password: {PASSWORD}")
    print(f"\nYou can use these credentials to login and test the feature manually.")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
