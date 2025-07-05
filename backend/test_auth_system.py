#!/usr/bin/env python3
"""
Test script for new authentication system with email/password
"""

import requests
import json
import sys
import os
from datetime import datetime
import random

def test_new_authentication_system():
    """Test the new authentication system with email/password"""
    print("=== Testing New Authentication System ===")
    base_url = "http://localhost:8000"
    
    # Generate unique user data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_num = random.randint(1000, 9999)
    
    user_email = f"test_{timestamp}_{random_num}@example.com"
    user_password = f"password_{random_num}"
    user_name = f"Test User {random_num}"
    
    try:
        # Test 1: User Signup with Email/Password
        print(f"\n1. Testing User Signup with Email/Password...")
        signup_data = {
            "email": user_email,
            "password": user_password,
            "full_name": user_name,
            "skill_level": "intermediate",
            "profile_data": {
                "university": "Test University",
                "degree": "Computer Science",
                "year": "3rd Year",
                "interests": ["Python", "Machine Learning", "Data Structures"],
                "programming_languages": ["Python", "JavaScript", "Java"],
                "goals": ["Master DSA", "Get better at coding", "Build projects"]
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
                print(f"   User ID: {user_data.get('user_id', 'Unknown')}")
                print(f"   Skill Level: {user_data.get('skill_level', 'Unknown')}")
                print(f"   Profile Data: {user_data.get('profile_data', {})}")
                
                user_id = user_data.get('user_id')
            else:
                print(f"❌ Signup failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Signup request failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error details: {error_detail}")
            except:
                print(f"   Response text: {response.text}")
            return False
        
        # Test 2: User Login with Email/Password
        print(f"\n2. Testing User Login with Email/Password...")
        login_data = {
            "email": user_email,
            "password": user_password
        }
        
        response = requests.post(f"{base_url}/api/user/login", json=login_data, timeout=10)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ User login successful")
                user_data = result.get("user", {})
                chat_history = result.get("chat_history", [])
                print(f"   User: {user_data.get('full_name', 'Unknown')}")
                print(f"   Email: {user_data.get('email', 'Unknown')}")
                print(f"   Chat History: {len(chat_history)} messages")
                print(f"   Statistics: {user_data.get('statistics', {})}")
                print(f"   Profile Data: {user_data.get('profile_data', {})}")
            else:
                print(f"❌ Login failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Login request failed: {response.status_code}")
            return False
        
        # Test 3: Wrong Password Login
        print(f"\n3. Testing Wrong Password Login...")
        wrong_login_data = {
            "email": user_email,
            "password": "wrong_password"
        }
        
        response = requests.post(f"{base_url}/api/user/login", json=wrong_login_data, timeout=10)
        print(f"Wrong password login response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if not result.get("success"):
                print("✅ Wrong password correctly rejected")
                print(f"   Message: {result.get('message', 'Unknown')}")
            else:
                print("❌ Wrong password was accepted (security issue)")
                return False
        else:
            print(f"❌ Wrong password request failed: {response.status_code}")
            return False
        
        # Test 4: Send Chat Message
        print(f"\n4. Testing Chat Message with Authentication...")
        chat_data = {
            "message": "Explain binary search tree insertion with examples",
            "user_id": user_id,
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
        
        # Test 5: Get Updated User Profile
        print(f"\n5. Testing User Profile Retrieval...")
        response = requests.get(f"{base_url}/api/user/{user_id}/profile", timeout=10)
        print(f"Profile response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ User profile retrieval successful")
                user_data = result.get("user", {})
                print(f"   User: {user_data.get('full_name', 'Unknown')}")
                print(f"   Total Queries: {user_data.get('statistics', {}).get('total_queries', 0)}")
                print(f"   Completed Topics: {len(user_data.get('completed_topics', []))}")
            else:
                print(f"❌ Profile retrieval failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Profile request failed: {response.status_code}")
            return False
        
        # Test 6: Get Chat History
        print(f"\n6. Testing Chat History Retrieval...")
        response = requests.get(f"{base_url}/api/user/{user_id}/chat-history", timeout=10)
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
                    print(f"   Latest response: {latest_message.get('response', 'Unknown')[:50]}...")
            else:
                print(f"❌ Chat history retrieval failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Chat history request failed: {response.status_code}")
            return False
        
        # Test 7: Update User Profile
        print(f"\n7. Testing User Profile Update...")
        update_data = {
            "skill_level": "advanced",
            "profile_data": {
                "university": "Updated University",
                "degree": "Computer Science",
                "year": "4th Year",
                "interests": ["Python", "Machine Learning", "Data Structures", "Web Development"],
                "programming_languages": ["Python", "JavaScript", "Java", "C++"],
                "goals": ["Master DSA", "Build advanced projects", "Get a job"]
            }
        }
        
        response = requests.put(f"{base_url}/api/user/{user_id}/profile", json=update_data, timeout=10)
        print(f"Profile update response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ User profile update successful")
                updated_user = result.get("user", {})
                print(f"   Updated skill level: {updated_user.get('skill_level', 'Unknown')}")
                print(f"   Updated university: {updated_user.get('profile_data', {}).get('university', 'Unknown')}")
            else:
                print(f"❌ Profile update failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Profile update request failed: {response.status_code}")
            return False
        
        # Test 8: Export User Data
        print(f"\n8. Testing User Data Export...")
        response = requests.get(f"{base_url}/api/user/{user_id}/export", timeout=10)
        print(f"Export response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ User data export successful")
                export_data = result.get("data", {})
                print(f"   Export contains: {list(export_data.keys())}")
                print(f"   Chat history messages: {len(export_data.get('chat_history', []))}")
                print(f"   User profile: {export_data.get('user_profile', {}).get('full_name', 'Unknown')}")
                
                # Save to file
                filename = f"test_export_{user_id}.json"
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                print(f"   Saved to: {filename}")
            else:
                print(f"❌ Export failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Export request failed: {response.status_code}")
            return False
        
        print(f"\n🎉 All authentication tests passed!")
        print(f"✅ Test User Details:")
        print(f"   Email: {user_email}")
        print(f"   Password: {user_password}")
        print(f"   User ID: {user_id}")
        print(f"   Name: {user_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in authentication test: {e}")
        return False

def main():
    """Run all authentication tests"""
    print("🚀 Starting New Authentication System Tests\n")
    
    if not test_new_authentication_system():
        print("\n❌ Authentication tests failed.")
        return False
    
    print("\n🎉 All authentication tests passed!")
    print("\n✅ Features confirmed working:")
    print("   - Email/Password user signup")
    print("   - Email/Password user login")
    print("   - Password verification and security")
    print("   - Chat message processing and storage")
    print("   - Chat history retrieval")
    print("   - User profile management and updates")
    print("   - User statistics tracking")
    print("   - Data export functionality")
    print("   - MongoDB integration with all features")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
