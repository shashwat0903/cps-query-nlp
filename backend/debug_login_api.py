#!/usr/bin/env python3
"""
Debug the login API call
"""

import requests
import json

def debug_login_api():
    """Debug the login API call"""
    print("🔍 Debugging login API call...")
    
    # Test with a new user that doesn't exist
    user_data = {
        "user_id": "debug_user_gmail_com",
        "email": "debug.user@gmail.com",
        "full_name": "Debug User"
    }
    
    print(f"📤 Sending request: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/user/login",
            json=user_data,
            timeout=10
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📝 Response data: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    debug_login_api()
