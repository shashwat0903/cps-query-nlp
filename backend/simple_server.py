from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import json
import traceback

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS setup to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "CPS Learning System API is running (Simple Mode)",
        "timestamp": datetime.now().isoformat()
    }

# Chat message model
class MessageRequest(BaseModel):
    message: str
    chat_history: Optional[List[Dict]] = []
    user_id: Optional[str] = "default"

@app.post("/api/chat")
async def chat(request: MessageRequest):
    """Handle chat messages with Groq API"""
    try:
        prompt = request.message
        user_id = request.user_id or "default"
        
        print(f"🔄 Processing chat message for user {user_id}")
        print(f"🔄 Prompt: {prompt}")
        
        # Get API key from environment
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {
                "response": "Error: GROQ_API_KEY not found in environment variables",
                "videos": [],
                "analysis": {"error": "Missing API key"}
            }
        
        # Use Groq API directly
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """You are an expert DSA (Data Structures and Algorithms) tutor. 
        Provide clear, concise explanations of concepts, include code examples when helpful, 
        and give practical learning advice. Keep responses focused and educational.
        Always be encouraging and supportive."""
        
        payload = {
            "model": "mistral-saba-24b",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2048,
            "top_p": 0.9
        }
        
        print("🔄 Sending request to Groq API...")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            print("✅ Received response from Groq API")
            
            return {
                "response": ai_response,
                "videos": [],
                "analysis": {"topic": prompt}
            }
        else:
            error_msg = f"Groq API error: {response.status_code} - {response.text}"
            print(f"❌ {error_msg}")
            return {
                "response": "Sorry, I encountered an error while processing your request.",
                "videos": [],
                "analysis": {"error": error_msg}
            }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "response": "Sorry, an error occurred while processing your request.",
            "videos": [],
            "analysis": {"error": str(e)}
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
