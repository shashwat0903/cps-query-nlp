#!/usr/bin/env python3
"""
Test MongoDB Atlas Connection and Integration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔄 Testing MongoDB Atlas Connection...")

try:
    # Test 1: Basic connection
    print("\n1. Testing basic MongoDB connection...")
    from database.models import db_config
    print(f"✅ Connected to database: {db_config.DATABASE_NAME}")
    
    # Test 2: Test user model
    print("\n2. Testing user model...")
    from database.models import user_model
    print("✅ User model initialized")
    
    # Test 3: Test chat history model
    print("\n3. Testing chat history model...")
    from database.models import chat_history_model
    print("✅ Chat history model initialized")
    
    # Test 4: Test learning session model
    print("\n4. Testing learning session model...")
    from database.models import learning_session_model
    print("✅ Learning session model initialized")
    
    # Test 5: Test database operations
    print("\n5. Testing database operations...")
    
    # Test user creation
    test_user_data = {
        'email': 'test@example.com',
        'password': 'test123',
        'full_name': 'Test User',
        'skill_level': 'beginner'
    }
    
    # Check if user already exists
    existing_user = user_model.get_user_by_email('test@example.com')
    if existing_user:
        print("✅ Test user already exists")
        user_id = existing_user['_id']
    else:
        user_id = user_model.create_user(test_user_data)
        print(f"✅ Created test user with ID: {user_id}")
    
    # Test chat history
    chat_id = chat_history_model.save_chat_message(
        user_id=user_id,
        message="Hello, this is a test message",
        response="Hello! I'm working with MongoDB Atlas!"
    )
    print(f"✅ Saved test chat message with ID: {chat_id}")
    
    # Test learning session
    session_data = {
        'current_path': ['Arrays', 'Searching', 'Sorting'],
        'current_step_index': 0,
        'target_topic': 'Data Structures'
    }
    
    session_id = learning_session_model.create_learning_session(user_id, session_data)
    print(f"✅ Created test learning session with ID: {session_id}")
    
    print("\n🎉 All MongoDB Atlas tests passed successfully!")
    print("✅ Your MongoDB integration is working perfectly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
