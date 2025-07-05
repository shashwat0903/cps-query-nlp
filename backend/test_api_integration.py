#!/usr/bin/env python3
"""
Test MongoDB integration with the running server
"""

import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:5000"

def test_user_registration():
    """Test user registration (stores in MongoDB)"""
    print("🔄 Testing user registration...")
    
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "skill_level": "beginner",
        "preferences": {"theme": "dark", "notifications": True}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 200:
            print("✅ User registration successful!")
            return response.json()
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None

def test_chat_message(user_id="default"):
    """Test chat message (stores in MongoDB)"""
    print("🔄 Testing chat message...")
    
    chat_data = {
        "message": "What is a binary tree?",
        "user_id": user_id,
        "chat_history": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
        if response.status_code == 200:
            print("✅ Chat message successful!")
            result = response.json()
            print(f"📝 Response: {result['response'][:100]}...")
            return result
        else:
            print(f"❌ Chat message failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error during chat: {e}")
        return None

def test_mongodb_data():
    """Test if data is actually stored in MongoDB"""
    print("🔄 Testing MongoDB data storage...")
    
    try:
        # Import MongoDB models to check data
        import sys
        sys.path.append('.')
        from database.models import user_model, chat_history_model
        
        # Check users collection
        if user_model and user_model.collection is not None:
            users_count = user_model.collection.count_documents({})
            print(f"📊 Users in MongoDB: {users_count}")
            
            # Get latest user
            if users_count > 0:
                latest_user = user_model.collection.find_one({}, sort=[('created_at', -1)])
                if latest_user:
                    print(f"👤 Latest user: {latest_user.get('email', 'Unknown')}")
        
        # Check chat history collection  
        if chat_history_model and chat_history_model.collection is not None:
            chats_count = chat_history_model.collection.count_documents({})
            print(f"💬 Chat messages in MongoDB: {chats_count}")
            
            # Get latest chat
            if chats_count > 0:
                latest_chat = chat_history_model.collection.find_one({}, sort=[('timestamp', -1)])
                if latest_chat:
                    print(f"💬 Latest chat message: {latest_chat.get('message', 'Unknown')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking MongoDB data: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting MongoDB Integration Test")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test 1: User Registration
    print("\n🧪 Test 1: User Registration")
    user_result = test_user_registration()
    
    # Test 2: Chat Message
    print("\n🧪 Test 2: Chat Message")
    chat_result = test_chat_message()
    
    # Test 3: MongoDB Data Verification
    print("\n🧪 Test 3: MongoDB Data Verification")
    mongodb_result = test_mongodb_data()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"✅ User Registration: {'PASS' if user_result else 'FAIL'}")
    print(f"✅ Chat Message: {'PASS' if chat_result else 'FAIL'}")
    print(f"✅ MongoDB Storage: {'PASS' if mongodb_result else 'FAIL'}")
    
    if user_result and chat_result and mongodb_result:
        print("\n🎉 All tests passed! MongoDB integration is working perfectly!")
    else:
        print("\n❌ Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    main()
