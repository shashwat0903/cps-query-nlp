#!/usr/bin/env python3
"""
Test the complete login flow with email and name
"""

import requests
import json
from datetime import datetime

def test_login_flow():
    """Test complete login flow with user creation"""
    print("🧪 Testing complete login flow...")
    
    # 1. Test login with new user (should create user)
    print("\n1️⃣ Testing login with new user...")
    new_user_data = {
        "user_id": "test_user_gmail_com",
        "email": "test.user@gmail.com",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/user/login",
            json=new_user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ New user login successful!")
                print(f"👤 Name: {data['user']['full_name']}")
                print(f"📧 Email: {data['user']['email']}")
                print(f"💬 Chat history: {len(data['chat_history'])} messages")
            else:
                print(f"❌ Login failed: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # 2. Test login with existing user (should not create duplicate)
    print("\n2️⃣ Testing login with existing user...")
    try:
        response = requests.post(
            "http://localhost:8000/api/user/login",
            json=new_user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ Existing user login successful!")
                print(f"👤 Name: {data['user']['full_name']}")
                print(f"📧 Email: {data['user']['email']}")
            else:
                print(f"❌ Login failed: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # 3. Test chat with the new user
    print("\n3️⃣ Testing chat with new user...")
    chat_data = {
        "message": "Hello! I want to learn about binary search trees.",
        "user_id": "test_user_gmail_com",
        "chat_history": []
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat API working!")
            print(f"📝 Response: {data['response'][:100]}...")
            if 'videos' in data and data['videos']:
                print(f"🎥 Videos: {len(data['videos'])} found")
        else:
            print(f"❌ Chat failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat failed: {e}")
    
    # 4. Test chat history retrieval
    print("\n4️⃣ Testing chat history retrieval...")
    try:
        response = requests.get(
            "http://localhost:8000/api/user/test_user_gmail_com/chat-history?limit=5",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat history retrieval successful!")
            print(f"📚 Total messages: {data['total_messages']}")
            if data['chat_history']:
                latest_msg = data['chat_history'][-1]
                print(f"🔍 Latest message: {latest_msg.get('message', '')[:50]}...")
        else:
            print(f"❌ Chat history failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat history failed: {e}")
    
    print("\n🎉 Login flow test completed!")

if __name__ == "__main__":
    test_login_flow()
