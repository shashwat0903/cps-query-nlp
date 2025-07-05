#!/usr/bin/env python3
"""
Update user profile with correct name and email
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_user_profile():
    """Update the default user with correct information"""
    try:
        print("🔄 Updating user profile...")
        
        # Import models
        from database.models import user_model
        
        # Update user data
        update_data = {
            "email": "ritesh.singh@iitrpr.ac.in",
            "full_name": "Ritesh Singh",
            "profile_data": {
                "university": "IIT Ropar",
                "degree": "Computer Science", 
                "year": "3rd Year",
                "interests": ["Machine Learning", "Data Structures", "Algorithms", "Web Development"],
                "programming_languages": ["Python", "JavaScript", "Java", "C++"]
            },
            "preferences": {
                "learning_style": "hands-on",
                "difficulty_preference": "intermediate",
                "time_per_session": 45,
                "preferred_topics": ["dynamic_programming", "graph_algorithms", "system_design"]
            }
        }
        
        # Update the user
        success = user_model.update_user("default", update_data)
        
        if success:
            print("✅ User profile updated successfully!")
            
            # Verify the update
            updated_user = user_model.get_user_by_id("default")
            if updated_user:
                print(f"📧 Email: {updated_user.get('email')}")
                print(f"👤 Name: {updated_user.get('full_name')}")
                print(f"🏫 University: {updated_user.get('profile_data', {}).get('university')}")
                print(f"🎓 Degree: {updated_user.get('profile_data', {}).get('degree')}")
            
            return True
        else:
            print("❌ Failed to update user profile")
            return False
            
    except Exception as e:
        print(f"❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_user_profile()
    if success:
        print("\n🎉 Profile updated successfully!")
        print("✅ MongoDB now has your correct information")
    else:
        print("\n❌ Update failed")
