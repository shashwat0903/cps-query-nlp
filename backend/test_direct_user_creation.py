#!/usr/bin/env python3
"""
Test direct user creation
"""

from database.models import user_model

def test_direct_user_creation():
    print("🧪 Testing direct user creation...")
    
    user_data = {
        'user_id': 'test_user2_gmail_com',
        'email': 'test.user2@gmail.com',
        'full_name': 'Test User 2',
        'skill_level': 'beginner',
        'completed_topics': [],
        'known_concepts': [],
        'preferences': {},
        'statistics': {'total_queries': 0, 'topics_completed': 0, 'total_study_time': 0}
    }
    
    user_id = user_model.create_user(user_data)
    print(f'Created user: {user_id}')
    
    if user_id:
        user = user_model.get_user_by_id(user_id)
        print(f'User: {user.get("full_name")} ({user.get("email")})')
    else:
        print("❌ Failed to create user")

if __name__ == "__main__":
    test_direct_user_creation()
