#!/usr/bin/env python3
"""
Test script specifically for signup and login functionality
"""

import requests
import json
import sys
import os
from datetime import datetime
import random

def test_fresh_user_signup_and_login():
    """Test signup and login with a fresh user"""
    print("=== Testing Fresh User Signup and Login ===")
    base_url = "http://localhost:8000"
    
    # Generate unique user data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_num = random.randint(1000, 9999)
    
    user_email = f"test_user_{timestamp}_{random_num}@example.com"
    user_id = user_email.replace('@', '_').replace('.', '_')
    user_name = f"Test User {random_num}"
    
    try:
        # Test 1: User Signup
        print(f"\n1. Testing User Signup for {user_name}...")
        signup_data = {
            "email": user_email,
            "full_name": user_name,
            "skill_level": "beginner",
            "profile_data": {
                "university": "Test University",
                "degree": "Computer Science",
                "year": "2nd Year",
                "interests": ["Python", "Data Structures", "Algorithms"],
                "programming_languages": ["Python", "JavaScript"],
                "goals": ["Learn DSA", "Get better at coding"]
            }
        }
        
        response = requests.post(f"{base_url}/api/user/signup", json=signup_data, timeout=10)
        print(f"Signup response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Signup result: {result}")
            
            if result.get("success"):
                print("✅ User signup successful")
                user_data = result.get("user", {})
                print(f"   User: {user_data.get('full_name', 'Unknown')}")
                print(f"   Email: {user_data.get('email', 'Unknown')}")
                print(f"   Skill Level: {user_data.get('skill_level', 'Unknown')}")
                print(f"   User ID: {user_data.get('user_id', 'Unknown')}")
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
        
        # Test 2: User Login
        print(f"\n2. Testing User Login for {user_name}...")
        login_data = {
            "user_id": user_id,
            "email": user_email,
            "full_name": user_name
        }
        
        response = requests.post(f"{base_url}/api/user/login", json=login_data, timeout=10)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Login result keys: {list(result.keys())}")
            
            if result.get("success"):
                print("✅ User login successful")
                user_data = result.get("user", {})
                print(f"   User: {user_data.get('full_name', 'Unknown')}")
                print(f"   Email: {user_data.get('email', 'Unknown')}")
                print(f"   Completed Topics: {len(user_data.get('completed_topics', []))}")
                print(f"   Profile Data: {user_data.get('profile_data', {})}")
                
                # Test 3: Send a chat message
                print(f"\n3. Testing Chat Message for {user_name}...")
                chat_data = {
                    "message": "What are arrays in Python?",
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
                    else:
                        print(f"❌ Chat failed: {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Chat request failed: {response.status_code}")
                    return False
                
                # Test 4: Export user data
                print(f"\n4. Testing User Data Export for {user_name}...")
                response = requests.get(f"{base_url}/api/user/{user_id}/export", timeout=10)
                print(f"Export response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print("✅ User data export successful")
                        export_data = result.get("data", {})
                        print(f"   Export contains: {list(export_data.keys())}")
                        
                        # Save to file
                        filename = f"test_export_{user_id}.json"
                        with open(filename, 'w') as f:
                            json.dump(export_data, f, indent=2, default=str)
                        print(f"   Saved to: {filename}")
                        
                        return True
                    else:
                        print(f"❌ Export failed: {result.get('message', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Export request failed: {response.status_code}")
                    return False
                    
            else:
                print(f"❌ Login failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Login request failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error details: {error_detail}")
            except:
                print(f"   Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

def test_google_auth_endpoints():
    """Test Google auth endpoints"""
    print("\n=== Testing Google Auth Endpoints ===")
    base_url = "http://localhost:8000"
    
    try:
        # Test Google auth redirect
        response = requests.get(f"{base_url}/auth/google", timeout=10)
        print(f"Google auth redirect status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Google auth redirect working: {result.get('message', 'Unknown')}")
        else:
            print(f"❌ Google auth redirect failed: {response.status_code}")
            return False
        
        # Test Google auth callback
        response = requests.get(f"{base_url}/auth/google/callback", timeout=10)
        print(f"Google auth callback status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Google auth callback working: {result.get('message', 'Unknown')}")
            return True
        else:
            print(f"❌ Google auth callback failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google auth: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Signup and Login Tests\n")
    
    # Test fresh user signup and login
    if not test_fresh_user_signup_and_login():
        print("\n❌ Signup/Login tests failed.")
        return False
    
    # Test Google auth endpoints
    if not test_google_auth_endpoints():
        print("\n❌ Google auth tests failed.")
        return False
    
    print("\n🎉 All signup and login tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
