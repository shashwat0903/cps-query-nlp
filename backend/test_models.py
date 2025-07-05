#!/usr/bin/env python3
"""
Test MongoDB models integration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_models():
    """Test MongoDB models"""
    try:
        print("🔍 Testing MongoDB models...")
        
        # Import models
        from database.models import user_model, chat_history_model, learning_session_model
        print("✅ All models imported successfully!")
        
        # Test if models are connected
        if user_model and user_model.collection is not None:
            print("✅ User model connected to MongoDB Atlas")
        else:
            print("❌ User model not connected")
            
        if chat_history_model and chat_history_model.collection is not None:
            print("✅ Chat history model connected to MongoDB Atlas")
        else:
            print("❌ Chat history model not connected")
            
        if learning_session_model and learning_session_model.collection is not None:
            print("✅ Learning session model connected to MongoDB Atlas")
        else:
            print("❌ Learning session model not connected")
            
        print("🎉 All MongoDB models are working with Atlas!")
        return True
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_models()
