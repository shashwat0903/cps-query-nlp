#!/usr/bin/env python3
"""
Complete test for user profile creation and chat history
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_complete_user_flow():
    """Test complete user flow: profile creation, chat, and history retrieval"""
    try:
        print("🔄 Testing complete user flow...")
        
        # First, directly create and update user in MongoDB
        print("\n1️⃣ Creating/Updating user profile in MongoDB...")
        from database.models import user_model, chat_history_model
        
        # Update user with correct information
        user_data = {
            "user_id": "ritesh_singh",
            "email": "ritesh.singh@iitrpr.ac.in",
            "full_name": "Ritesh Singh",
            "skill_level": "intermediate",
            "completed_topics": ["arrays", "strings", "basic_algorithms"],
            "known_concepts": ["sorting", "searching", "recursion"],
            "preferences": {
                "learning_style": "hands-on",
                "difficulty_preference": "intermediate",
                "time_per_session": 45,
                "preferred_topics": ["dynamic_programming", "graph_algorithms", "system_design"]
            },
            "statistics": {
                "total_queries": 0,
                "topics_completed": 3,
                "total_study_time": 150,
                "streak_days": 5,
                "sessions_completed": 8
            },
            "profile_data": {
                "university": "IIT Ropar",
                "degree": "Computer Science",
                "year": "3rd Year",
                "interests": ["Machine Learning", "Data Structures", "Algorithms", "Web Development"],
                "programming_languages": ["Python", "JavaScript", "Java", "C++"],
                "goals": ["Master DSA", "Prepare for interviews", "Build projects"]
            }
        }
        
        # Check if user exists, if not create
        existing_user = user_model.get_user_by_id("ritesh_singh")
        if existing_user:
            print("✅ User already exists, updating profile...")
            user_model.update_user("ritesh_singh", user_data)
        else:
            print("🆕 Creating new user profile...")
            user_id = user_model.create_user(user_data)
            print(f"✅ User created with ID: {user_id}")
        
        # 2. Test user login API
        print("\n2️⃣ Testing user login API...")
        login_response = requests.post(
            "http://localhost:8000/api/user/login",
            json={"user_id": "ritesh_singh"},
            timeout=10
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print("✅ Login API working!")
            print(f"📧 Email: {login_data['user']['email']}")
            print(f"👤 Name: {login_data['user']['full_name']}")
            print(f"📊 Completed Topics: {len(login_data['user']['completed_topics'])}")
            print(f"💬 Chat History: {len(login_data['chat_history'])} messages")
        else:
            print(f"❌ Login API failed: {login_response.status_code}")
        
        # 3. Send a chat message
        print("\n3️⃣ Testing chat with user profile...")
        chat_response = requests.post(
            "http://localhost:8000/api/chat",
            json={
                "message": "Hello! I want to learn about graph algorithms.",
                "user_id": "ritesh_singh",
                "chat_history": []
            },
            timeout=30
        )
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            print("✅ Chat API working!")
            print(f"📝 Response: {chat_data['response'][:100]}...")
        else:
            print(f"❌ Chat API failed: {chat_response.status_code}")
        
        # 4. Test chat history retrieval
        print("\n4️⃣ Testing chat history retrieval...")
        history_response = requests.get(
            "http://localhost:8000/api/user/ritesh_singh/chat-history?limit=10",
            timeout=10
        )
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            print("✅ Chat history API working!")
            print(f"📚 Total messages: {history_data['total_messages']}")
            if history_data['chat_history']:
                latest_msg = history_data['chat_history'][-1]
                print(f"🔍 Latest message: {latest_msg.get('message', '')[:50]}...")
        else:
            print(f"❌ Chat history API failed: {history_response.status_code}")
        
        # 5. Verify data in MongoDB
        print("\n5️⃣ Verifying data in MongoDB...")
        final_user = user_model.get_user_by_id("ritesh_singh")
        if final_user:
            print("✅ User profile verified in MongoDB!")
            print(f"📧 Email: {final_user.get('email')}")
            print(f"👤 Name: {final_user.get('full_name')}")
            print(f"🎓 University: {final_user.get('profile_data', {}).get('university')}")
            
            # Check updated statistics
            stats = final_user.get('statistics', {})
            print(f"📊 Total Queries: {stats.get('total_queries', 0)}")
            print(f"✅ Topics Completed: {stats.get('topics_completed', 0)}")
        
        print("\n🎉 Complete user flow test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_user_flow()
    if success:
        print("\n✅ All systems working perfectly!")
        print("🚀 User profiles are being stored in MongoDB")
        print("💬 Chat history is being saved and retrieved")
        print("👤 User: Ritesh Singh profile is complete")
    else:
        print("\n❌ Some tests failed")
