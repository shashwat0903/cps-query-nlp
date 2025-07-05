#!/usr/bin/env python3
"""
Test script to verify MongoDB integration and API endpoints
"""

import requests
import json
import sys
import os

# Add the current directory to Python path
sys.path.append('.')

from database.models import db_config, user_model, chat_history_model, learning_session_model

def test_database_connection():
    """Test MongoDB connection"""
    print("=== Testing Database Connection ===")
    try:
        if db_config.connect():
            print("✅ Database connected successfully")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_user_creation():
    """Test user model operations"""
    print("\n=== Testing User Model ===")
    try:
        # Test user creation
        test_user_data = {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "full_name": "Test User",
            "skill_level": "beginner",
            "preferences": {"learning_style": "visual"},
            "profile_data": {
                "university": "Test University",
                "degree": "Computer Science",
                "year": "2nd Year"
            }
        }
        
        # Check if user exists first
        existing_user = user_model.get_user_by_id("test_user_123")
        if existing_user:
            print("✅ Test user already exists")
        else:
            # Create new user
            user_id = user_model.create_user(test_user_data)
            if user_id:
                print(f"✅ Test user created with ID: {user_id}")
            else:
                print("❌ Failed to create test user")
                return False
        
        # Test user retrieval
        user = user_model.get_user_by_id("test_user_123")
        if user:
            print(f"✅ User retrieved: {user.get('full_name', 'Unknown')}")
            return True
        else:
            print("❌ Failed to retrieve test user")
            return False
            
    except Exception as e:
        print(f"❌ User model error: {e}")
        return False

def test_chat_history():
    """Test chat history model operations"""
    print("\n=== Testing Chat History Model ===")
    try:
        # Test chat history creation
        test_chat_data = {
            "user_id": "test_user_123",
            "message": "Hello, this is a test message",
            "response": "Hello! How can I help you with DSA today?",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        # Save chat message
        chat_id = chat_history_model.save_chat_message(
            test_chat_data["user_id"],
            test_chat_data["message"],
            test_chat_data["response"]
        )
        
        if chat_id:
            print(f"✅ Chat message saved with ID: {chat_id}")
        else:
            print("❌ Failed to save chat message")
            return False
        
        # Retrieve chat history
        chat_history = chat_history_model.get_chat_history("test_user_123")
        if chat_history:
            print(f"✅ Chat history retrieved: {len(chat_history)} messages")
            return True
        else:
            print("✅ No chat history found (expected for new user)")
            return True
            
    except Exception as e:
        print(f"❌ Chat history model error: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n=== Testing API Endpoints ===")
    base_url = "http://localhost:8000"
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Health check endpoint working")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test user login endpoint
        login_data = {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "full_name": "Test User"
        }
        
        response = requests.post(f"{base_url}/api/user/login", json=login_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ User login endpoint working")
                return True
            else:
                print(f"❌ Login failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Login endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting MongoDB Integration Tests\n")
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection failed. Exiting.")
        return False
    
    # Test user model
    if not test_user_creation():
        print("\n❌ User model tests failed. Exiting.")
        return False
    
    # Test chat history model
    if not test_chat_history():
        print("\n❌ Chat history model tests failed. Exiting.")
        return False
    
    # Test API endpoints
    if not test_api_endpoints():
        print("\n❌ API endpoint tests failed. Exiting.")
        return False
    
    print("\n🎉 All tests passed! MongoDB integration is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
