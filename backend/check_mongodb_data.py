#!/usr/bin/env python3
"""
Check MongoDB data to verify everything is being stored
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_mongodb_data():
    """Check what data is stored in MongoDB"""
    try:
        print("🔄 Checking MongoDB data...")
        
        # Import models
        from database.models import user_model, chat_history_model, learning_session_model
        
        # Check user data
        print("\n👤 USER DATA:")
        user = user_model.get_user_by_id("default")
        if user:
            print(f"  📧 Email: {user.get('email')}")
            print(f"  👤 Name: {user.get('full_name')}")
            print(f"  🎓 Skill Level: {user.get('skill_level')}")
            print(f"  📊 Completed Topics: {len(user.get('completed_topics', []))}")
            print(f"  📈 Total Queries: {user.get('statistics', {}).get('total_queries', 0)}")
        else:
            print("  ❌ No user found")
        
        # Check chat history
        print("\n💬 CHAT HISTORY:")
        chat_history = chat_history_model.get_chat_history("default", limit=5)
        print(f"  📝 Total messages: {len(chat_history)}")
        for i, chat in enumerate(chat_history[-3:], 1):  # Show last 3
            print(f"  {i}. Message: {chat.get('message', '')[:50]}...")
            print(f"     Response: {chat.get('response', '')[:50]}...")
        
        # Check learning sessions
        print("\n📚 LEARNING SESSION:")
        session = learning_session_model.get_active_session("default")
        if session:
            print(f"  🎯 Current Path: {session.get('current_path', [])}")
            print(f"  📊 Progress: {session.get('current_step_index', 0)}")
            print(f"  ✅ Completed: {len(session.get('completed_topics', []))}")
        else:
            print("  ❌ No active learning session")
        
        print("\n🎉 MongoDB data check complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_mongodb_data()
