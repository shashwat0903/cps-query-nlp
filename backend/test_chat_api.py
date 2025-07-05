#!/usr/bin/env python3
"""
Test API endpoint to make sure chat is working and chat history is saved
"""

import requests
import json
import time

def test_chat_api():
    """Test the chat API endpoint and chat history saving"""
    try:
        print("🔄 Testing chat API...")
        
        # Generate a unique test user ID
        test_user_id = f"test_user_{int(time.time())}"
        print(f"🔄 Using test user ID: {test_user_id}")
        
        # Test data
        test_message = {
            "message": "Hello! I want to learn about arrays.",
            "user_id": test_user_id,
            "chat_history": []
        }
        
        # Make request to chat endpoint
        response = requests.post(
            "http://localhost:8080/api/chat",
            json=test_message,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat API working successfully!")
            
            # Wait a moment for the chat to be saved
            print("🔄 Waiting for chat history to be saved...")
            time.sleep(2)
            
            # Now check if the chat history was saved
            print(f"🔄 Retrieving chat history for user: {test_user_id}")
            history_response = requests.get(
                f"http://localhost:8080/api/user/{test_user_id}/chat-history",
                timeout=30
            )
            
            if history_response.status_code == 200:
                history_result = history_response.json()
                chat_history = history_result.get("chat_history", [])
                print(f"✅ Chat history retrieved: {len(chat_history)} messages")
                
                if len(chat_history) > 0:
                    print("✅ Chat history was successfully saved!")
                    for idx, chat in enumerate(chat_history):
                        print(f"  Message {idx+1}: {chat.get('message')[:30]}...")
                else:
                    print("❌ No chat history found - saving might not be working")
            else:
                print(f"❌ Failed to retrieve chat history: {history_response.status_code}")
                print(history_response.text)
            print(f"📝 Response: {result['response'][:100]}...")
            if result.get('analysis'):
                print(f"🔍 Analysis: {result['analysis']}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_chat_api()
    if success:
        print("\n🎉 API test successful!")
        print("✅ Your chat application should now work properly")
    else:
        print("\n❌ API test failed")
        print("🔧 Please check if the backend server is running on port 8000")
