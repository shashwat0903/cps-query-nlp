import requests
import json

def test_chat_api():
    url = "http://localhost:5000/api/chat"
    payload = {
        "message": "Explain binary search",
        "user_id": "default"
    }
    
    try:
        print("Sending request to API...")
        response = requests.post(url, json=payload)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_chat_api()
