#!/usr/bin/env python3
"""
Test script for MongoDB integration
"""

import sys
import os
from datetime import datetime
from database.models import user_model, chat_history_model, learning_session_model

def test_mongodb_integration():
    """Test MongoDB integration with user, chat history, and learning sessions."""
    print("🧪 Testing MongoDB Integration...")
    
    # Test 1: Create a test user
    print("\n1. Testing User Model...")
    test_user_data = {
        'email': 'test@example.com',
        'password': 'testpassword123',
        'full_name': 'Test User',
        'skill_level': 'beginner',
        'preferences': {'theme': 'dark', 'notifications': True}
    }
    
    user_id = user_model.create_user(test_user_data)
    if user_id:
        print(f"✅ User created successfully with ID: {user_id}")
        
        # Test getting user
        user = user_model.get_user_by_id(user_id)
        if user:
            print(f"✅ User retrieved successfully: {user['full_name']}")
        else:
            print("❌ Failed to retrieve user")
    else:
        print("❌ Failed to create user")
        return False
    
    # Test 2: Chat History
    print("\n2. Testing Chat History Model...")
    chat_id = chat_history_model.save_chat_message(
        user_id=user_id,
        message="What is a binary tree?",
        response="A binary tree is a hierarchical data structure...",
        analysis={'topic': 'binary tree', 'difficulty': 'intermediate'}
    )
    
    if chat_id:
        print(f"✅ Chat message saved successfully with ID: {chat_id}")
        
        # Test getting chat history
        history = chat_history_model.get_chat_history(user_id, limit=5)
        if history:
            print(f"✅ Chat history retrieved: {len(history)} messages")
        else:
            print("❌ Failed to retrieve chat history")
    else:
        print("❌ Failed to save chat message")
    
    # Test 3: Learning Sessions
    print("\n3. Testing Learning Session Model...")
    session_data = {
        'current_path': ['Arrays', 'Linked Lists', 'Trees'],
        'current_step_index': 0,
        'target_topic': 'Trees',
        'completed_topics': []
    }
    
    session_id = learning_session_model.create_learning_session(user_id, session_data)
    if session_id:
        print(f"✅ Learning session created successfully with ID: {session_id}")
        
        # Test getting active session
        session = learning_session_model.get_active_session(user_id)
        if session:
            print(f"✅ Active session retrieved: {session['target_topic']}")
        else:
            print("❌ Failed to retrieve active session")
    else:
        print("❌ Failed to create learning session")
    
    # Test 4: Update user progress
    print("\n4. Testing User Update...")
    update_success = user_model.update_user(user_id, {
        'completed_topics': ['Arrays'],
        'statistics.topics_completed': 1
    })
    
    if update_success:
        print("✅ User progress updated successfully")
        
        # Verify update
        updated_user = user_model.get_user_by_id(user_id)
        if updated_user and 'Arrays' in updated_user.get('completed_topics', []):
            print("✅ User progress verified")
        else:
            print("❌ User progress update not reflected")
    else:
        print("❌ Failed to update user progress")
    
    print("\n🎉 MongoDB Integration Test Complete!")
    return True

if __name__ == "__main__":
    try:
        test_mongodb_integration()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
