import requests
import json

def test_groq_server_api():
    url = "http://localhost:8000/api/chat"
    payload = {
        "message": "Explain binary search algorithm",
        "user_id": "test_user"
    }
    
    print("Sending request to Groq server API...")
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse:")
            print("="*50)
            print(data.get("response", "No response"))
            print("="*50)
            print("\nAnalysis:", data.get("analysis", {}))
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The server took too long to respond.")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_groq_server_api()
