#!/usr/bin/env python3
"""
Enhanced User Profile Creation and Management
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
from database.models import user_model, chat_history_model, learning_session_model

class UserProfileManager:
    """Manages user profiles with MongoDB integration"""
    
    def __init__(self):
        self.user_model = user_model
        self.chat_history_model = chat_history_model
        self.learning_session_model = learning_session_model
    
    def create_default_user(self, user_id: str = "default", email: str = "ritesh.singh@example.com", full_name: str = "Ritesh Singh") -> Optional[Dict]:
        """Create a default user profile based on student profile"""
        try:
            # Check if user already exists
            existing_user = self.user_model.get_user_by_id(user_id)
            if existing_user:
                return existing_user
            
            # Create comprehensive user profile
            user_data = {
                "user_id": user_id,
                "email": email,
                "full_name": full_name,
                "skill_level": "beginner",
                "completed_topics": [],
                "known_concepts": [],
                "preferences": {
                    "learning_style": "visual",
                    "difficulty_preference": "intermediate",
                    "time_per_session": 30,
                    "preferred_topics": ["arrays", "strings", "algorithms"]
                },
                "learning_goals": [
                    "Master data structures and algorithms",
                    "Prepare for technical interviews",
                    "Build strong problem-solving skills"
                ],
                "statistics": {
                    "total_queries": 0,
                    "topics_completed": 0,
                    "total_study_time": 0,
                    "last_active": datetime.now(timezone.utc),
                    "streak_days": 0,
                    "average_session_time": 0
                },
                "profile_data": {
                    "university": "IIT Ropar",
                    "degree": "Computer Science",
                    "year": "3rd Year",
                    "interests": ["Machine Learning", "Web Development", "Data Structures"],
                    "programming_languages": ["Python", "JavaScript", "Java", "C++"]
                }
            }
            
            # Create user in MongoDB
            user_id_created = self.user_model.create_user(user_data)
            if user_id_created:
                print(f"✅ Created default user: {full_name} ({email})")
                return self.user_model.get_user_by_id(user_id_created)
            else:
                print("❌ Failed to create default user")
                return None
                
        except Exception as e:
            print(f"❌ Error creating default user: {e}")
            return None
    
    def initialize_user_learning_session(self, user_id: str) -> Optional[Dict]:
        """Initialize learning session for user"""
        try:
            # Create initial learning session
            session_data = {
                "current_path": [],
                "current_step_index": 0,
                "target_topic": None,
                "completed_topics": [],
                "session_start": datetime.now(timezone.utc),
                "learning_objectives": [
                    "Understand basic data structures",
                    "Learn algorithm analysis",
                    "Practice problem solving"
                ],
                "progress_tracking": {
                    "topics_explored": [],
                    "videos_watched": [],
                    "concepts_mastered": []
                }
            }
            
            session_id = self.learning_session_model.create_learning_session(user_id, session_data)
            if session_id:
                print(f"✅ Created learning session for user: {user_id}")
                return self.learning_session_model.get_active_session(user_id)
            else:
                print("❌ Failed to create learning session")
                return None
                
        except Exception as e:
            print(f"❌ Error creating learning session: {e}")
            return None
    
    def setup_complete_user_profile(self, user_id: str = "default", email: str = "ritesh.singh@example.com", full_name: str = "Ritesh Singh") -> bool:
        """Setup complete user profile with all necessary data"""
        try:
            print(f"🔄 Setting up complete profile for {full_name}...")
            
            # Create user
            user = self.create_default_user(user_id, email, full_name)
            if not user:
                return False
            
            # Create learning session
            session = self.initialize_user_learning_session(user_id)
            if not session:
                return False
            
            # Add some sample chat history to get started
            if self.chat_history_model:
                self.chat_history_model.save_chat_message(
                    user_id=user_id,
                    message="Hello! I'm ready to start learning DSA.",
                    response="Welcome to your DSA learning journey! I'm here to help you master data structures and algorithms. What would you like to learn first?",
                    analysis={
                        "intent": "greeting",
                        "user_level": "beginner",
                        "setup_complete": True
                    }
                )
            
            print(f"✅ Complete profile setup successful for {full_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up complete profile: {e}")
            return False

# Initialize the profile manager
profile_manager = UserProfileManager()

if __name__ == "__main__":
    # Setup the complete user profile
    success = profile_manager.setup_complete_user_profile(
        user_id="default",
        email="ritesh.singh@iitrpr.ac.in", 
        full_name="Ritesh Singh"
    )
    
    if success:
        print("🎉 User profile setup complete!")
        print("📊 MongoDB collections updated with user data")
        print("🚀 Ready to start learning!")
    else:
        print("❌ Profile setup failed")
