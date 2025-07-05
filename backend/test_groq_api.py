import os
import requests
from dotenv import load_dotenv

def test_groq_api():
    # Load environment variables from .env
    load_dotenv()
    
    # Get Groq API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ ERROR: GROQ_API_KEY not found in environment variables")
        return
    
    print(f"✅ GROQ_API_KEY found (first 5 chars: {groq_api_key[:5]}...)")
    
    # Set up headers and payload
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """You are an expert DSA (Data Structures and Algorithms) tutor. 
    Provide clear, concise explanations of concepts, include code examples when helpful, 
    and give practical learning advice. Keep responses focused and educational."""
    
    payload = {
        "model": "mistral-saba-24b",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": "Explain binary search in simple terms"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 500,
        "top_p": 0.9
    }
    
    # Send request to Groq API
    print("🔄 Sending request to Groq API...")
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"🔄 Response status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! Received response from Groq API:")
            print("="*50)
            print(result["choices"][0]["message"]["content"].strip())
            print("="*50)
            print("\nAPI response metadata:")
            print(f"Model: {result.get('model', 'unknown')}")
            print(f"Usage: {result.get('usage', {})}")
        else:
            print(f"❌ ERROR: API returned status code {response.status_code}")
            print("Response content:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out. The API took too long to respond.")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Connection error. Could not connect to the Groq API.")
    except Exception as e:
        print(f"❌ ERROR: An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    test_groq_api()
