#!/usr/bin/env python3
"""
Simple test to create user profile and test MongoDB integration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_user_creation():
    """Test creating a user and testing MongoDB integration"""
    try:
        print("🔄 Testing MongoDB integration...")
        
        # Import models
        from database.models import user_model, chat_history_model, learning_session_model
        print("✅ Models imported successfully")
        
        # Create test user
        user_data = {
            "user_id": "default",
            "email": "ritesh.singh@iitrpr.ac.in",
            "full_name": "Ritesh Singh",
            "skill_level": "intermediate",
            "completed_topics": ["arrays", "strings"],
            "known_concepts": ["basic_algorithms", "data_structures"],
            "preferences": {
                "learning_style": "visual",
                "difficulty_preference": "intermediate",
                "time_per_session": 30
            },
            "statistics": {
                "total_queries": 0,
                "topics_completed": 2,
                "total_study_time": 120
            },
            "profile_data": {
                "university": "IIT Ropar",
                "degree": "Computer Science",
                "year": "3rd Year"
            }
        }
        
        # Check if user exists
        existing_user = user_model.get_user_by_id("default")
        if existing_user:
            print("✅ User 'default' already exists")
            print(f"📧 Email: {existing_user.get('email')}")
            print(f"👤 Name: {existing_user.get('full_name')}")
        else:
            print("🔄 Creating new user...")
            user_id = user_model.create_user(user_data)
            if user_id:
                print(f"✅ User created with ID: {user_id}")
            else:
                print("❌ Failed to create user")
                return False
        
        # Test chat history
        print("🔄 Testing chat history...")
        chat_id = chat_history_model.save_chat_message(
            user_id="default",
            message="Hello! I want to learn about trees.",
            response="Great! Trees are hierarchical data structures. Let me explain...",
            analysis={"topic": "trees", "intent": "learning"}
        )
        
        if chat_id:
            print("✅ Chat message saved successfully")
        else:
            print("❌ Failed to save chat message")
        
        # Get recent chat history
        recent_chats = chat_history_model.get_recent_context("default", limit=3)
        print(f"📚 Recent chats: {len(recent_chats)} messages")
        
        print("🎉 MongoDB integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_user_creation()
    if success:
        print("\n✅ Ready to test the application!")
        print("🌐 Open your browser and test the chat functionality")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
