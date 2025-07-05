#!/usr/bin/env python3
"""
Test user creation and lookup specifically
"""

from database.models import user_model

def test_user_creation_and_lookup():
    print("🧪 Testing user creation and lookup...")
    
    # Test with a specific user_id
    user_id = "test_lookup_user"
    
    # Check if user exists
    existing_user = user_model.get_user_by_id(user_id)
    if existing_user:
        print(f"✅ User {user_id} already exists: {existing_user.get('full_name')} ({existing_user.get('email')})")
        return
    
    # Create new user
    user_data = {
        'user_id': user_id,
        'email': 'test.lookup@gmail.com',
        'full_name': 'Test Lookup User',
        'skill_level': 'beginner',
        'completed_topics': [],
        'known_concepts': [],
        'preferences': {},
        'statistics': {'total_queries': 0, 'topics_completed': 0, 'total_study_time': 0}
    }
    
    created_user_id = user_model.create_user(user_data)
    print(f'Created user with ID: {created_user_id}')
    
    if created_user_id:
        # Now try to look up by user_id
        user = user_model.get_user_by_id(user_id)
        if user:
            print(f'✅ Lookup by user_id successful: {user.get("full_name")} ({user.get("email")})')
        else:
            print(f'❌ Lookup by user_id failed')
            
        # Try to look up by ObjectId
        user_by_obj_id = user_model.get_user_by_id(created_user_id)
        if user_by_obj_id:
            print(f'✅ Lookup by ObjectId successful: {user_by_obj_id.get("full_name")} ({user_by_obj_id.get("email")})')
        else:
            print(f'❌ Lookup by ObjectId failed')
    else:
        print("❌ Failed to create user")

if __name__ == "__main__":
    test_user_creation_and_lookup()
