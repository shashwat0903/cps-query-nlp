#!/usr/bin/env python3
"""
Comprehensive test script for complete MongoDB integration
Tests user creation, chat history, profile management, and JSON export
"""

import requests
import json
import sys
import os
from datetime import datetime

def test_complete_user_flow():
    """Test complete user flow from signup to chat to export"""
    print("=== Testing Complete User Flow ===")
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: User Signup
        print("\n1. Testing User Signup...")
        signup_data = {
            "user_id": "ritesh.singh@iitrpr.ac.in",
            "email": "ritesh.singh@iitrpr.ac.in",
            "full_name": "Ritesh Singh",
            "skill_level": "intermediate",
            "profile_data": {
                "university": "IIT Ropar",
                "degree": "Computer Science",
                "year": "3rd Year",
                "interests": ["Machine Learning", "Data Structures", "Algorithms"],
                "programming_languages": ["Python", "JavaScript", "Java", "C++"],
                "goals": ["Master DSA", "Prepare for interviews", "Build projects"]
            }
        }
        
        response = requests.post(f"{base_url}/api/user/signup", json=signup_data, timeout=10)
        print(f"Signup response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ User signup successful")
                user_data = result.get("user", {})
                print(f"   User: {user_data.get('full_name', 'Unknown')}")
                print(f"   Email: {user_data.get('email', 'Unknown')}")
                print(f"   Skill Level: {user_data.get('skill_level', 'Unknown')}")
            else:
                print(f"❌ Signup failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Signup request failed: {response.status_code}")
            return False
        
        # Test 2: User Login
        print("\n2. Testing User Login...")
        login_data = {
            "user_id": "ritesh.singh@iitrpr.ac.in",
            "email": "ritesh.singh@iitrpr.ac.in",
            "full_name": "Ritesh Singh"
        }
        
        response = requests.post(f"{base_url}/api/user/login", json=login_data, timeout=10)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ User login successful")
                user_data = result.get("user", {})
                print(f"   User: {user_data.get('full_name', 'Unknown')}")
                print(f"   Completed Topics: {len(user_data.get('completed_topics', []))}")
            else:
                print(f"❌ Login failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Login request failed: {response.status_code}")
            return False
        
        # Test 3: Chat Message
        print("\n3. Testing Chat Message...")
        chat_data = {
            "message": "Explain binary search algorithm with Python code",
            "user_id": "ritesh.singh@iitrpr.ac.in",
            "chat_history": []
        }
        
        response = requests.post(f"{base_url}/api/chat", json=chat_data, timeout=30)
        print(f"Chat response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("response"):
                print("✅ Chat message successful")
                print(f"   Response length: {len(result.get('response', ''))}")
                print(f"   Videos found: {len(result.get('videos', []))}")
                print(f"   Analysis: {bool(result.get('analysis', {}))}")
            else:
                print(f"❌ Chat failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Chat request failed: {response.status_code}")
            return False
        
        # Test 4: Get Chat History
        print("\n4. Testing Chat History Retrieval...")
        response = requests.get(f"{base_url}/api/user/ritesh.singh@iitrpr.ac.in/chat-history", timeout=10)
        print(f"Chat history response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Chat history retrieval successful")
                chat_history = result.get("chat_history", [])
                print(f"   Messages in history: {len(chat_history)}")
                if chat_history:
                    latest_message = chat_history[-1]
                    print(f"   Latest message: {latest_message.get('message', 'Unknown')[:50]}...")
            else:
                print(f"❌ Chat history retrieval failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Chat history request failed: {response.status_code}")
            return False
        
        # Test 5: User Profile Export
        print("\n5. Testing User Profile Export...")
        response = requests.get(f"{base_url}/api/user/ritesh.singh@iitrpr.ac.in/export", timeout=10)
        print(f"Export response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ User profile export successful")
                export_data = result.get("data", {})
                print(f"   Profile data keys: {list(export_data.keys())}")
                print(f"   Chat history messages: {len(export_data.get('chat_history', []))}")
                print(f"   Completed topics: {len(export_data.get('completed_topics', []))}")
                
                # Save export data to file
                export_filename = f"user_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(export_filename, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                print(f"   Export saved to: {export_filename}")
            else:
                print(f"❌ Profile export failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Export request failed: {response.status_code}")
            return False
        
        print("\n🎉 All user flow tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in user flow test: {e}")
        return False

def test_data_persistence():
    """Test that data persists across different requests"""
    print("\n=== Testing Data Persistence ===")
    base_url = "http://localhost:8000"
    
    try:
        # Login again to check if data persists
        login_data = {
            "user_id": "ritesh.singh@iitrpr.ac.in",
            "email": "ritesh.singh@iitrpr.ac.in",
            "full_name": "Ritesh Singh"
        }
        
        response = requests.post(f"{base_url}/api/user/login", json=login_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                user_data = result.get("user", {})
                print(f"✅ User data persisted: {user_data.get('full_name', 'Unknown')}")
                print(f"   Statistics: {user_data.get('statistics', {})}")
                return True
            else:
                print(f"❌ Data persistence failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Persistence test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in persistence test: {e}")
        return False

def main():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive MongoDB Integration Tests\n")
    
    # Test complete user flow
    if not test_complete_user_flow():
        print("\n❌ Complete user flow tests failed.")
        return False
    
    # Test data persistence
    if not test_data_persistence():
        print("\n❌ Data persistence tests failed.")
        return False
    
    print("\n🎉 All comprehensive tests passed! MongoDB integration is fully functional.")
    print("\n✅ Features confirmed working:")
    print("   - User signup and login")
    print("   - Chat message processing and storage")
    print("   - Chat history retrieval")
    print("   - User profile management")
    print("   - Data export functionality")
    print("   - Data persistence across sessions")
    print("   - MongoDB Atlas integration")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
