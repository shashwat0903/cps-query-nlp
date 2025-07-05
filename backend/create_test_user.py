"""
Create a test user for login testing
"""
from database.models import user_model
import bcrypt
import os
import sys
from datetime import datetime

def create_test_user():
    try:
        print("🔄 Creating test user...")
        
        # Check if user already exists
        existing = user_model.get_user_by_email("test@example.com")
        if existing:
            print("✅ Test user already exists")
            return True
            
        # Generate a hashed password
        password = "password123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = {
            "user_id": "test_user",
            "email": "test@example.com",
            "password": hashed_password,  # Will be hashed by create_user
            "full_name": "Test User",
            "skill_level": "beginner",
            "completed_topics": [],
            "known_concepts": [],
            "current_learning_path": [],
            "preferences": {
                "difficulty_preference": "beginner",
                "learning_style": "mixed",
                "topics_of_interest": [],
                "time_per_session": 30
            },
            "statistics": {
                "total_queries": 0,
                "topics_completed": 0,
                "total_study_time": 0,
                "streak_days": 0,
                "sessions_completed": 0,
                "last_active": datetime.now().isoformat()
            },
            "profile_data": {
                "university": "Test University",
                "degree": "Computer Science",
                "year": "2023",
                "interests": ["Algorithms", "Data Structures"],
                "programming_languages": ["Python", "JavaScript"],
                "goals": ["Learn DSA"]
            },
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Create the user
        success = user_model.create_user(user)
        if success:
            print(f"✅ Test user created successfully: email='test@example.com', password='password123'")
            return True
        else:
            print("❌ Failed to create test user")
            return False
    except Exception as e:
        print(f"❌ Error creating test user: {str(e)}")
        return False

if __name__ == "__main__":
    create_test_user()
    print("\nYou can now login with:")
    print("Email: test@example.com")
    print("Password: password123")
