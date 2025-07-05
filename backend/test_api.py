#!/usr/bin/env python3
"""
Test Backend API and MongoDB Storage
"""

import requests
import json
import time

def test_backend_api():
    """Test backend API endpoints and MongoDB storage"""
    
    print("🔍 Testing Backend API and MongoDB Storage...")
    
    base_url = "http://localhost:5000"
    
    # Test 1: Register a new user
    print("\n1️⃣ Testing User Registration...")
    register_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "skill_level": "beginner"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=register_data)
        print(f"Registration response: {response.status_code}")
        if response.status_code == 200:
            print("✅ User registration successful!")
            user_data = response.json()
            print(f"User created: {user_data.get('user', {}).get('email')}")
        else:
            print(f"❌ Registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Test 2: Login user
    print("\n2️⃣ Testing User Login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            print("✅ User login successful!")
            login_result = response.json()
            token = login_result.get('access_token')
            user_id = login_result.get('user', {}).get('id')
            print(f"User logged in: {login_result.get('user', {}).get('email')}")
            print(f"Token received: {token[:30]}..." if token else "No token")
        else:
            print(f"❌ Login failed: {response.text}")
            token = None
            user_id = None
    except Exception as e:
        print(f"❌ Login error: {e}")
        token = None
        user_id = None
    
    # Test 3: Send chat message
    print("\n3️⃣ Testing Chat Message (MongoDB storage)...")
    chat_data = {
        "message": "I want to learn about binary trees",
        "user_id": user_id or "test_user_123",
        "chat_history": []
    }
    
    try:
        response = requests.post(f"{base_url}/api/chat", json=chat_data)
        print(f"Chat response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Chat message processed successfully!")
            chat_result = response.json()
            print(f"Response: {chat_result.get('response', '')[:100]}...")
            print(f"Videos found: {len(chat_result.get('videos', []))}")
        else:
            print(f"❌ Chat failed: {response.text}")
    except Exception as e:
        print(f"❌ Chat error: {e}")
    
    # Test 4: Get user info (to verify MongoDB storage)
    if token and user_id:
        print("\n4️⃣ Testing User Info Retrieval...")
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(f"{base_url}/api/auth/user", headers=headers)
            print(f"User info response: {response.status_code}")
            if response.status_code == 200:
                print("✅ User info retrieved successfully!")
                user_info = response.json()
                print(f"User email: {user_info.get('email')}")
                print(f"Completed topics: {len(user_info.get('completed_topics', []))}")
                print(f"Total queries: {user_info.get('statistics', {}).get('total_queries', 0)}")
            else:
                print(f"❌ User info retrieval failed: {response.text}")
        except Exception as e:
            print(f"❌ User info error: {e}")
    
    print("\n🎉 Backend API and MongoDB test completed!")

if __name__ == "__main__":
    test_backend_api()
