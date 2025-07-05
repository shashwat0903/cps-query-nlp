#!/usr/bin/env python3
"""
Test chat handler user creation methods
"""

from queryHandling.integrated_chat_handler import IntegratedChatHandler

def test_chat_handler_user_creation():
    print("🧪 Testing chat handler user creation...")
    
    # Initialize chat handler
    chat_handler = IntegratedChatHandler()
    
    # Test user creation with info
    user_id = "test_chat_handler_user"
    email = "test.chathandler@gmail.com"
    full_name = "Test Chat Handler User"
    
    print(f"🔄 Testing create_user_profile_with_info...")
    user_profile = chat_handler.create_user_profile_with_info(user_id, email, full_name)
    
    if user_profile:
        print(f"✅ User profile created: {user_profile.get('full_name')} ({user_profile.get('email')})")
        print(f"👤 User ID: {user_profile.get('user_id')}")
        
        # Now test loading the profile
        print(f"🔄 Testing load_user_profile...")
        loaded_profile = chat_handler.load_user_profile(user_id)
        
        if loaded_profile:
            print(f"✅ Profile loaded: {loaded_profile.get('full_name')} ({loaded_profile.get('email')})")
        else:
            print(f"❌ Failed to load profile")
    else:
        print("❌ Failed to create user profile")

if __name__ == "__main__":
    test_chat_handler_user_creation()
