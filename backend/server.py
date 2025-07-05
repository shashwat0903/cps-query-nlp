from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from queryHandling.integrated_chat_handler import IntegratedChatHandler
from routes.auth import router as auth_router
from typing import List, Dict, Optional
from datetime import datetime
from database.models import user_model, chat_history_model, learning_session_model
import bcrypt

app = FastAPI()

# Initialize the integrated chat handler
chat_handler = IntegratedChatHandler()

# Include auth routes
app.include_router(auth_router)

# CORS setup to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://cps-query-nlp.vercel.app",  # Vercel production URL
        "https://cps-query-nlp-*.vercel.app"  # Vercel preview deployments
    ],
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
        "message": "CPS Learning System API is running",
        "timestamp": datetime.now().isoformat(),
        "database_status": "connected" if user_model.collection else "disconnected",
        "version": "1.0.0",
        "environment": "production"
    }

@app.get("/status", include_in_schema=True)
async def status_page():
    """Status page with HTML output for easy viewing"""
    db_status = "connected" if user_model.collection else "disconnected"
    timestamp = datetime.now().isoformat()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CPS Query NLP Backend Status</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                margin: 40px auto;
                max-width: 650px;
                line-height: 1.6;
                font-size: 18px;
                color: #444;
                padding: 0 10px;
                background-color: #f9f9f9;
            }}
            h1, h2 {{
                line-height: 1.2;
                color: #333;
            }}
            .status {{
                padding: 15px;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .healthy {{
                background-color: #d4edda;
                border-color: #c3e6cb;
                color: #155724;
            }}
            .warning {{
                background-color: #fff3cd;
                border-color: #ffeeba;
                color: #856404;
            }}
            .error {{
                background-color: #f8d7da;
                border-color: #f5c6cb;
                color: #721c24;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: 150px 1fr;
                gap: 10px;
                margin: 20px 0;
            }}
            .label {{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <h1>CPS Query NLP Backend Status</h1>
        
        <div class="status {'healthy' if db_status == 'connected' else 'error'}">
            <h2>Status: {'Healthy' if db_status == 'connected' else 'Error'}</h2>
            <p>The backend API is {'running normally' if db_status == 'connected' else 'experiencing issues'}.</p>
        </div>
        
        <div class="info-grid">
            <span class="label">API Version:</span>
            <span>1.0.0</span>
            
            <span class="label">Environment:</span>
            <span>Production</span>
            
            <span class="label">Database:</span>
            <span>{db_status}</span>
            
            <span class="label">Timestamp:</span>
            <span>{timestamp}</span>
        </div>
        
        <p>This page is used to verify the backend deployment status.</p>
        <p><small>CPS Query NLP System &copy; 2025</small></p>
    </body>
    </html>
    """
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)

class MessageRequest(BaseModel):
    message: str
    chat_history: Optional[List[Dict]] = []
    user_id: Optional[str] = "default"

@app.post("/api/chat")
async def chat(request: MessageRequest):
    """Handle chat messages and save to MongoDB"""
    try:
        prompt = request.message
        chat_history = request.chat_history or []
        user_id = request.user_id or "default"
        
        print(f"🔄 Processing chat message for user {user_id}")
        print(f"🔄 Prompt: {prompt}")
        print(f"🔄 Chat history: {chat_history}")
        
        # Use the integrated chat handler with enhanced parameters
        result = chat_handler.handle_chat_message(
            message=prompt,
            chat_history=chat_history,
            user_id=user_id
        )
        print(f"🔄 Chat handler result: {result}")
        
        # Save chat message to MongoDB
        if result.get('response'):
            chat_message_id = chat_history_model.save_chat_message(
                user_id=user_id,
                message=prompt,
                response=result.get('response'),
                analysis=result.get('analysis', {})
            )
            
            if chat_message_id:
                print(f"✅ Chat message saved with ID: {chat_message_id}")
                
                # Update user statistics if user exists
                try:
                    user = user_model.get_user_by_id(user_id)
                    if user:
                        current_queries = user.get('statistics', {}).get('total_queries', 0)
                        user_model.update_user(user_id, {
                            'statistics.total_queries': current_queries + 1,
                            'statistics.last_active': datetime.now().isoformat()
                        })
                        print(f"✅ Updated user statistics for user: {user_id}")
                except Exception as stats_err:
                    print(f"⚠️ Could not update user statistics: {stats_err}")
        else:
            print(f"⚠️ No response from chat handler. Result: {result}")
        
        return {
            "response": result.get('response', 'Sorry, I could not process your request.'),
            "videos": result.get('videos', []),
            "analysis": result.get('analysis', {}),
            "error": result.get('error')
        }
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "response": "Sorry, an error occurred while processing your request.",
            "videos": [],
            "analysis": {},
            "error": str(e)
        }

# Pydantic models for requests
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserSignupRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str  # Make password required
    skill_level: Optional[str] = "beginner"
    profile_data: Optional[Dict] = {}

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    skill_level: Optional[str] = None
    profile_data: Optional[Dict] = {}
    statistics: Optional[Dict] = {}

@app.post("/api/user/login")
async def user_login(request: UserLoginRequest):
    """Handle user login with email and password verification"""
    try:
        print(f"🔄 Login attempt for {request.email}")
        
        # Get user by email
        user = user_model.get_user_by_email(request.email)
        if not user:
            return {
                "success": False,
                "message": "User not found. Please check your email or sign up.",
                "user": None,
                "chat_history": []
            }
        
        # Verify password
        if not user_model.verify_password(request.password, user.get('password')):
            return {
                "success": False,
                "message": "Invalid password. Please try again.",
                "user": None,
                "chat_history": []
            }
        
        # Update last active time
        user_id = user.get('_id')  # This is likely the MongoDB ObjectId as a string
        user_model.update_user(user_id, {
            'statistics.last_active': datetime.now().isoformat()
        })
        
        # Get chat history for the user
        chat_history = chat_history_model.get_chat_history(user_id, limit=20)
        
        # Remove password from response
        user.pop('password', None)
        
        print(f"✅ Login successful for {user.get('full_name', 'User')}")
        print(f"✅ User ID: {user_id}")
        print(f"✅ Chat history count: {len(chat_history)}")
        print(f"✅ First chat message: {chat_history[0] if chat_history else 'None'}")
        
        # Format user profile for response
        user_profile = {
            "user_id": user_id,  # Use the MongoDB _id as the user_id
            "email": user.get('email'),
            "full_name": user.get('full_name'),
            "skill_level": user.get('skill_level', 'beginner'),
            "completed_topics": user.get('completed_topics', []),
            "known_concepts": user.get('known_concepts', []),
            "statistics": user.get('statistics', {}),
            "profile_data": user.get('profile_data', {}),
            "preferences": user.get('preferences', {})
        }
        
        print(f"✅ Returning user profile: {user_profile}")
        
        return {
            "success": True,
            "message": f"Welcome back, {user.get('full_name', 'User')}!",
            "user": user_profile,
            "chat_history": chat_history
        }
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return {
            "success": False,
            "message": f"Login failed: {str(e)}",
            "user": None,
            "chat_history": []
        }

@app.get("/api/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get detailed user profile from MongoDB"""
    try:
        print(f"🔄 Getting user profile for user_id: {user_id}")
        user_profile = user_model.get_user_by_id(user_id)
        
        if not user_profile:
            print(f"❌ User not found for user_id: {user_id}")
            return {"success": False, "message": "User not found"}
        
        # Remove password from response
        user_profile.pop('password', None)
        
        # Ensure user_id is included in the response
        if '_id' in user_profile and 'user_id' not in user_profile:
            user_profile['user_id'] = user_profile['_id']
            
        print(f"✅ Found user profile for: {user_profile.get('email', 'Unknown')}")
        return {
            "success": True,
            "user": user_profile
        }
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
        return {"success": False, "message": str(e)}

@app.get("/api/user/{user_id}/chat-history")
async def get_user_chat_history(user_id: str, limit: int = 20):
    """Get user's chat history from MongoDB"""
    try:
        print(f"🔄 Fetching chat history for user: {user_id}, limit: {limit}")
        
        # Try to find the user first to verify they exist
        user = user_model.get_user_by_id(user_id)
        if not user:
            print(f"⚠️ User not found with ID: {user_id}, but will try to get chat history anyway")
        else:
            print(f"✅ Found user: {user.get('email')} with ID: {user_id}")
        
        # Get chat history
        chat_history = chat_history_model.get_chat_history(user_id, limit=limit)
        print(f"✅ Found {len(chat_history)} chat messages for user: {user_id}")
        
        return {
            "success": True,
            "chat_history": chat_history,
            "total_messages": len(chat_history)
        }
    except Exception as e:
        print(f"❌ Error fetching chat history: {e}")
        return {"success": False, "message": str(e), "chat_history": []}

@app.post("/api/user/signup")
async def user_signup(request: UserSignupRequest):
    """Handle user signup and create comprehensive profile with password"""
    try:
        # Check if user already exists
        existing_user = user_model.get_user_by_email(request.email)
        if existing_user:
            return {
                "success": False,
                "message": "User with this email already exists. Please log in instead.",
                "user": None
            }
        
        # Create user ID from email
        user_id = request.email.replace('@', '_').replace('.', '_')
        
        print(f"🔄 Creating new user profile for {request.full_name} ({request.email})")
        
        # Enhanced profile data
        enhanced_profile_data = {
            "university": "",
            "degree": "",
            "year": "",
            "interests": [],
            "programming_languages": [],
            "goals": [],
            **(request.profile_data or {})
        }
        
        # Create comprehensive user profile
        user_profile = {
            "user_id": user_id,
            "email": request.email,
            "full_name": request.full_name,
            "password": request.password,  # Will be hashed in create_user
            "skill_level": request.skill_level,
            "completed_topics": [],
            "known_concepts": [],
            "current_learning_path": [],
            "preferences": {
                "difficulty_preference": request.skill_level,
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
            "profile_data": enhanced_profile_data,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Save to database (password will be hashed automatically)
        result = user_model.create_user(user_profile)
        
        if result:
            print(f"✅ User profile created successfully for {request.full_name}")
            print(f"✅ User ID from create_user: {result}")
            
            # Get the created user (without password)
            created_user = user_model.get_user_by_email(request.email)
            if created_user:
                # Remove password from response
                created_user.pop('password', None)
                
                # Use the MongoDB _id as the user_id
                user_id = created_user.get('_id')
                print(f"✅ MongoDB _id for new user: {user_id}")
                
                # Get empty chat history for new user
                chat_history = []
                
                return {
                    "success": True,
                    "message": f"Welcome {request.full_name}! Your profile has been created.",
                    "user": {
                        "user_id": user_id,
                        "email": created_user.get('email'),
                        "full_name": created_user.get('full_name'),
                        "skill_level": created_user.get('skill_level', 'beginner'),
                        "completed_topics": created_user.get('completed_topics', []),
                        "known_concepts": created_user.get('known_concepts', []),
                        "statistics": created_user.get('statistics', {}),
                        "profile_data": created_user.get('profile_data', {})
                    },
                    "chat_history": chat_history
                }
        
        return {
            "success": False,
            "message": "Failed to create user profile",
            "user": None,
            "chat_history": []
        }
            
    except Exception as e:
        print(f"❌ Signup error: {str(e)}")
        return {
            "success": False,
            "message": f"Signup failed: {str(e)}",
            "user": None
        }

@app.put("/api/user/{user_id}/profile")
async def update_user_profile(user_id: str, request: UserUpdateRequest):
    """Update user profile information in MongoDB"""
    try:
        # Load existing profile
        existing_profile = user_model.get_user_by_id(user_id)
        if not existing_profile:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Prepare update data
        update_data = {}
        if request.full_name:
            update_data["full_name"] = request.full_name
        if request.skill_level:
            update_data["skill_level"] = request.skill_level
        if request.profile_data:
            # Merge profile data
            current_profile_data = existing_profile.get("profile_data", {})
            current_profile_data.update(request.profile_data)
            update_data["profile_data"] = current_profile_data
        if request.statistics:
            # Merge statistics
            current_stats = existing_profile.get("statistics", {})
            current_stats.update(request.statistics)
            update_data["statistics"] = current_stats
        
        update_data["last_updated"] = datetime.now().isoformat()
        
        # Save updated profile
        result = user_model.update_user(user_id, update_data)
        
        if result:
            # Get updated profile
            updated_profile = user_model.get_user_by_id(user_id)
            if updated_profile:
                # Remove password from response
                updated_profile.pop('password', None)
                
                return {
                    "success": True,
                    "message": "Profile updated successfully",
                    "user": updated_profile
                }
        
        return {
            "success": False,
            "message": "Failed to update profile"
        }
            
    except Exception as e:
        print(f"❌ Profile update error: {str(e)}")
        return {
            "success": False,
            "message": f"Profile update failed: {str(e)}"
        }

@app.get("/api/user/{user_id}/export")
async def export_user_data(user_id: str):
    """Export all user data as JSON and save to MongoDB"""
    try:
        # Load user profile
        user_profile = user_model.get_user_by_id(user_id)
        if not user_profile:
            return {
                "success": False,
                "message": "User not found",
                "data": None
            }
        
        # Remove password from export
        user_profile.pop('password', None)
        
        # Get chat history
        chat_history = chat_history_model.get_chat_history(user_id, limit=1000)  # Get all chat history
        
        # Create comprehensive export data
        export_data = {
            "user_profile": user_profile,
            "chat_history": chat_history,
            "export_metadata": {
                "export_date": datetime.now().isoformat(),
                "export_version": "1.0",
                "total_messages": len(chat_history),
                "user_id": user_id
            },
            "statistics": user_profile.get("statistics", {}),
            "completed_topics": user_profile.get("completed_topics", []),
            "profile_data": user_profile.get("profile_data", {})
        }
        
        # Save export data to MongoDB as backup
        try:
            from database.models import db_config
            exports_collection = db_config.db["user_exports"]
            export_record = {
                "user_id": user_id,
                "export_data": export_data,
                "created_at": datetime.now(),
                "file_size": len(str(export_data))
            }
            exports_collection.insert_one(export_record)
            print(f"✅ Export data saved to MongoDB for user {user_id}")
        except Exception as e:
            print(f"⚠️ Warning: Could not save export to MongoDB: {e}")
        
        return {
            "success": True,
            "message": f"Data exported successfully for {user_profile.get('full_name', user_id)}",
            "data": export_data
        }
        
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        return {
            "success": False,
            "message": f"Export failed: {str(e)}",
            "data": None
        }

# Google OAuth endpoints for frontend compatibility
@app.get("/auth/google")
async def google_auth_redirect():
    """Google OAuth redirect endpoint"""
    return {
        "message": "Google OAuth should be handled by frontend Firebase",
        "status": "redirect_to_frontend"
    }

@app.get("/auth/google/callback")
async def google_auth_callback():
    """Google OAuth callback endpoint"""
    return {
        "message": "Google OAuth callback should be handled by frontend Firebase",
        "status": "redirect_to_frontend"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
