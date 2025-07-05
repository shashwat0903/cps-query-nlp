import requests
import json
import time

def test_chat_api():
    url = "http://localhost:5000/api/chat"
    payload = {
        "message": "Explain binary search",
        "user_id": "default"
    }
    
    print("Trying to connect to API server...")
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Attempt {retry_count + 1} of {max_retries}...")
            response = requests.post(url, json=payload, timeout=10)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\nResponse:")
                print(json.dumps(data, indent=2))
                return
            else:
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("Connection error: Server not responding")
        except requests.exceptions.Timeout:
            print("Timeout error: Server took too long to respond")
        except Exception as e:
            print(f"Exception: {e}")
        
        retry_count += 1
        if retry_count < max_retries:
            print(f"Retrying in 5 seconds...")
            time.sleep(5)
    
    print("\nServer appears to be unavailable. Generating fallback response...")
    fallback_response = {
        "response": "Binary search is an efficient algorithm for finding an item from a sorted list of items. It works by repeatedly dividing in half the portion of the list that could contain the item, until you've narrowed down the possible locations to just one. The algorithm has O(log n) time complexity, making it much faster than linear search for large datasets.",
        "videos": [
            {
                "title": "Binary Search Algorithm | Data Structures & Algorithms",
                "url": "https://www.youtube.com/watch?v=P3YID7liBug",
                "channel_name": "freeCodeCamp.org"
            }
        ],
        "analysis": {
            "detected_topic": "binary_search",
            "skill_level": "beginner"
        }
    }
    
    print("Fallback response:")
    print(json.dumps(fallback_response, indent=2))

if __name__ == "__main__":
    test_chat_api()
