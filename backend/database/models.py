"""
MongoDB Database Configuration and Models
"""

import os
import ssl
import certifi
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import bcrypt
from bson import ObjectId
import json

from database.db_utils import get_mongodb_client, get_async_mongodb_client

class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        # MongoDB connection string (you can customize this)
        self.MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME", "cps_learning_system")
        
        # Collections
        self.USERS_COLLECTION = "users"
        self.CHAT_HISTORY_COLLECTION = "chat_history"
        self.LEARNING_SESSIONS_COLLECTION = "learning_sessions"
        self.USER_PROGRESS_COLLECTION = "user_progress"
        
        # Initialize clients
        self.client = None
        self.async_client = None
        self.db = None
        self.async_db = None
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            # Use our utility function for a more robust connection
            self.client = get_mongodb_client(self.MONGODB_URI)
            self.db = self.client[self.DATABASE_NAME]
            print(f"✅ Connected to MongoDB: {self.DATABASE_NAME}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    def connect_async(self):
        """Connect to MongoDB asynchronously"""
        try:
            # Use our utility function for a more robust connection
            self.async_client = get_async_mongodb_client(self.MONGODB_URI)
            self.async_db = self.async_client[self.DATABASE_NAME]
            print(f"✅ Connected to MongoDB (async): {self.DATABASE_NAME}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB (async): {e}")
            return False
    
    def check_and_reconnect(self):
        """Check connection and reconnect if needed"""
        try:
            if self.client and self.db:
                # Test connection with a quick ping
                self.client.admin.command('ping')
                return True
            else:
                print("⚠️ No active MongoDB connection, reconnecting...")
                return self.connect()
        except Exception as e:
            print(f"⚠️ MongoDB connection check failed: {e}")
            print("🔄 Attempting to reconnect...")
            return self.connect()
    
    def close(self):
        """Close database connections"""
        if self.client:
            self.client.close()
        if self.async_client:
            self.async_client.close()

class UserModel:
    """User model for MongoDB operations"""
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.collection = None
        self.ensure_collection()
    
    def ensure_collection(self):
        """Ensure collection is available and reconnect if needed"""
        if self.collection is None:
            # First try to use the existing connection
            if self.db_config.db is not None:
                self.collection = self.db_config.db[self.db_config.USERS_COLLECTION]
                print(f"✅ User collection initialized from existing connection")
            else:
                # Try to reconnect
                if self.db_config.check_and_reconnect():
                    self.collection = self.db_config.db[self.db_config.USERS_COLLECTION]
                    print(f"✅ User collection initialized after reconnection")
                else:
                    print(f"❌ Failed to initialize user collection")
        return self.collection is not None
    
    def create_user(self, user_data: Dict) -> str:
        """Create a new user"""
        try:
            # Ensure collection is available
            if not self.ensure_collection():
                print("❌ Cannot create user: collection not available")
                return None
            
            # Hash password if provided
            if 'password' in user_data:
                print(f"🔄 Hashing password for user: {user_data.get('email')}")
                user_data['password'] = self._hash_password(user_data['password'])
                print(f"✅ Password hashed successfully")
            
            # Add metadata
            user_data.update({
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'is_active': True,
                'completed_topics': user_data.get('completed_topics', []),
                'current_learning_path': user_data.get('current_learning_path', []),
                'known_concepts': user_data.get('known_concepts', []),
                'skill_level': user_data.get('skill_level', 'beginner'),
                'preferences': user_data.get('preferences', {}),
                'statistics': user_data.get('statistics', {
                    'total_queries': 0,
                    'topics_completed': 0,
                    'total_study_time': 0,
                    'last_active': datetime.now(timezone.utc).isoformat()
                })
            })
            
            print(f"🔄 Inserting user into database: {user_data.get('email')}")
            result = self.collection.insert_one(user_data)
            print(f"✅ User created with ID: {result.inserted_id}")
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            # Ensure collection is available
            if not self.ensure_collection():
                print(f"❌ Cannot get user by ID: collection not available")
                return None
                
            # Try ObjectId first, then string user_id
            user = None
            if ObjectId.is_valid(user_id):
                user = self.collection.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                user = self.collection.find_one({"user_id": user_id})
            
            if not user:
                user = self.collection.find_one({"email": user_id})
            
            if user:
                user['_id'] = str(user['_id'])
                # Ensure all required fields exist
                if 'completed_topics' not in user:
                    user['completed_topics'] = []
                if 'known_concepts' not in user:
                    user['known_concepts'] = []
                if 'statistics' not in user:
                    user['statistics'] = {
                        'total_queries': 0,
                        'topics_completed': 0,
                        'total_study_time': 0,
                        'last_active': datetime.now(timezone.utc)
                    }
            return user
        
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            # Try to reconnect and try again
            if self.db_config.check_and_reconnect():
                self.collection = self.db_config.db[self.db_config.USERS_COLLECTION]
                return self.get_user_by_id(user_id)
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            # Ensure collection is available
            if not self.ensure_collection():
                print(f"❌ Cannot get user by email: collection not available")
                return None
            
            # Attempt to find the user with more detailed logging
            print(f"🔍 Looking up user with email: {email}")
            user = self.collection.find_one({"email": email})
            
            if user:
                print(f"✅ Found user with email: {email}")
                user['_id'] = str(user['_id'])
            else:
                print(f"⚠️ No user found with email: {email}")
                
            return user
        
        except Exception as e:
            print(f"❌ Error getting user by email: {e}")
            print(f"Database status: Connected: {self.db_config.client is not None}, DB: {self.db_config.db is not None}, Collection: {self.collection is not None}")
            # Try to reconnect and try again
            if self.db_config.check_and_reconnect():
                self.collection = self.db_config.db[self.db_config.USERS_COLLECTION]
                return self.get_user_by_email(email)
            return None
    
    def update_user(self, user_id: str, update_data: Dict) -> bool:
        """Update user information"""
        try:
            update_data['updated_at'] = datetime.now(timezone.utc)
            
            if ObjectId.is_valid(user_id):
                result = self.collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}
                )
            else:
                result = self.collection.update_one(
                    {"user_id": user_id},
                    {"$set": update_data}
                )
            
            return result.modified_count > 0
        
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            return False
    
    def update_user_progress(self, user_id: str, completed_topic: str, known_concepts: List[str] = None) -> bool:
        """Update user's learning progress"""
        try:
            update_data = {
                'updated_at': datetime.now(timezone.utc),
                'statistics.last_active': datetime.now(timezone.utc)
            }
            
            # Add completed topic
            if completed_topic:
                update_data['$addToSet'] = {'completed_topics': completed_topic}
                update_data['$inc'] = {'statistics.topics_completed': 1}
            
            # Update known concepts
            if known_concepts:
                update_data['known_concepts'] = known_concepts
            
            if ObjectId.is_valid(user_id):
                result = self.collection.update_one(
                    {"_id": ObjectId(user_id)},
                    update_data
                )
            else:
                result = self.collection.update_one(
                    {"user_id": user_id},
                    update_data
                )
            
            return result.modified_count > 0
        
        except Exception as e:
            print(f"❌ Error updating user progress: {e}")
            return False
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        try:
            print(f"🔄 Verifying password...")
            
            # Check if the hashed password is already bytes, if not convert it
            if isinstance(hashed_password, str):
                print(f"🔄 Converting string hashed password to bytes")
                hashed_password = hashed_password.encode('utf-8')
                
            # Ensure plain_password is encoded
            print(f"🔄 Encoding plain password")
            encoded_password = plain_password.encode('utf-8')
            
            result = bcrypt.checkpw(encoded_password, hashed_password)
            print(f"✅ Password verification result: {result}")
            return result
        except Exception as e:
            print(f"❌ Error verifying password: {e}")
            return False
    
    def _hash_password(self, password: str) -> bytes:
        """Hash password"""
        try:
            print(f"🔄 Hashing password")
            # Ensure password is encoded before hashing
            if isinstance(password, str):
                password = password.encode('utf-8')
                
            hashed = bcrypt.hashpw(password, bcrypt.gensalt())
            print(f"✅ Password hashed successfully")
            return hashed
        except Exception as e:
            print(f"❌ Error hashing password: {e}")
            raise e

class ChatHistoryModel:
    """Chat history model for MongoDB operations"""
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.collection = None
        self.ensure_collection()
    
    def ensure_collection(self):
        """Ensure collection is available and reconnect if needed"""
        if self.collection is None:
            # First try to use the existing connection
            if self.db_config.db is not None:
                self.collection = self.db_config.db[self.db_config.CHAT_HISTORY_COLLECTION]
                print(f"✅ Chat history collection initialized from existing connection")
            else:
                # Try to reconnect
                if self.db_config.check_and_reconnect():
                    self.collection = self.db_config.db[self.db_config.CHAT_HISTORY_COLLECTION]
                    print(f"✅ Chat history collection initialized after reconnection")
                else:
                    print(f"❌ Failed to initialize chat history collection")
        return self.collection is not None
    
    def save_chat_message(self, user_id: str, message: str, response: str, analysis: Dict = None) -> str:
        """Save a chat message and response"""
        try:
            # Ensure collection is available
            if not self.ensure_collection():
                print(f"❌ Cannot save chat message: collection not available")
                return None
                
            print(f"🔄 Saving chat message for user_id: {user_id}")
            
            # Ensure we're using a consistent user_id format
            actual_user_id = user_id
            
            # If it's a MongoDB ObjectId, get the user to verify and use the same ID format consistently
            if ObjectId.is_valid(user_id):
                print(f"✅ Valid ObjectId detected for chat save")
                user = user_model.get_user_by_id(user_id)
                if user:
                    print(f"✅ Found user with _id: {user_id}, email: {user.get('email')}")
                    # Use the _id since we found a user with it, but convert to string to ensure consistency
                    actual_user_id = str(user_id)
            
            print(f"✅ Using user_id {actual_user_id} for chat message")
            
            # Create the chat data with both user_id and a reference to the MongoDB _id
            chat_data = {
                'user_id': actual_user_id,
                'message': message,
                'response': response,
                'analysis': analysis or {},
                'timestamp': datetime.now(timezone.utc),
                'session_id': self._generate_session_id(actual_user_id)
            }
            
            result = self.collection.insert_one(chat_data)
            print(f"✅ Chat message saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"❌ Error saving chat message: {e}")
            return None
    
    def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a user"""
        try:
            # Ensure collection is available
            if not self.ensure_collection():
                print(f"❌ Cannot get chat history: collection not available")
                return []
                
            print(f"🔄 Getting chat history for user_id: {user_id}, limit: {limit}")
            
            # Try multiple query approaches to ensure we find all relevant messages
            query = {"$or": [{"user_id": user_id}]}
            
            # If user_id might be an ObjectId from MongoDB
            if ObjectId.is_valid(user_id):
                print(f"✅ Valid ObjectId detected for chat history query")
                # Also look for messages where user_id is the string representation of the ObjectId
                query["$or"].append({"user_id": str(user_id)})
                
                # Check if any users have this _id and get their email as an alternative lookup
                user = user_model.get_user_by_id(user_id)
                if user and 'email' in user:
                    print(f"✅ Found user with _id: {user_id}, email: {user.get('email')}")
                    # Also look for messages linked to this user's email
                    query["$or"].append({"user_id": user.get('email')})
            
            print(f"🔄 Executing chat history query: {query}")
            
            history = list(self.collection.find(query)
                        .sort("timestamp", -1)
                        .limit(limit))
            
            print(f"✅ Found {len(history)} chat messages")
            
            # Convert ObjectId to string
            for chat in history:
                chat['_id'] = str(chat['_id'])
            
            return list(reversed(history))  # Return in chronological order
        
        except Exception as e:
            print(f"❌ Error getting chat history: {e}")
            return []
    
    def get_recent_context(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent chat context for continuity"""
        try:
            recent_chats = list(self.collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit))
            
            context = []
            for chat in reversed(recent_chats):  # Chronological order
                context.append({
                    'role': 'user',
                    'content': chat['message']
                })
                context.append({
                    'role': 'assistant',
                    'content': chat['response']
                })
            
            return context
        
        except Exception as e:
            print(f"❌ Error getting recent context: {e}")
            return []
    
    def _generate_session_id(self, user_id: str) -> str:
        """Generate session ID based on user and current date"""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"{user_id}_{today}"

class LearningSessionModel:
    """Learning session model for MongoDB operations"""
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.collection = None
        self.ensure_collection()
    
    def ensure_collection(self):
        """Ensure collection is available and reconnect if needed"""
        if self.collection is None:
            # First try to use the existing connection
            if self.db_config.db is not None:
                self.collection = self.db_config.db[self.db_config.LEARNING_SESSIONS_COLLECTION]
                print(f"✅ Learning session collection initialized from existing connection")
            else:
                # Try to reconnect
                if self.db_config.check_and_reconnect():
                    self.collection = self.db_config.db[self.db_config.LEARNING_SESSIONS_COLLECTION]
                    print(f"✅ Learning session collection initialized after reconnection")
                else:
                    print(f"❌ Failed to initialize learning session collection")
        return self.collection is not None
    
    def create_learning_session(self, user_id: str, session_data: Dict) -> str:
        """Create a new learning session"""
        try:
            # Ensure collection is available
            if not self.ensure_collection():
                print(f"❌ Cannot create learning session: collection not available")
                return None
            
            session_data.update({
                'user_id': user_id,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'is_active': True,
                'progress': 0.0
            })
            
            result = self.collection.insert_one(session_data)
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"❌ Error creating learning session: {e}")
            return None
    
    def get_active_session(self, user_id: str) -> Optional[Dict]:
        """Get active learning session for user"""
        try:
            session = self.collection.find_one({
                "user_id": user_id,
                "is_active": True
            })
            
            if session:
                session['_id'] = str(session['_id'])
            return session
        
        except Exception as e:
            print(f"❌ Error getting active session: {e}")
            return None
    
    def update_session_progress(self, session_id: str, progress_data: Dict) -> bool:
        """Update learning session progress"""
        try:
            progress_data['updated_at'] = datetime.now(timezone.utc)
            
            result = self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": progress_data}
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            print(f"❌ Error updating session progress: {e}")
            return False

# Database instance (singleton pattern)
db_config = DatabaseConfig()
connection_success = db_config.connect()
print(f"🔄 Initial database connection attempt: {'✅ Success' if connection_success else '❌ Failed'}")

# Model instances
user_model = UserModel(db_config)
chat_history_model = ChatHistoryModel(db_config)
learning_session_model = LearningSessionModel(db_config)

# Ensure collections are initialized
user_model.ensure_collection()
chat_history_model.ensure_collection()
learning_session_model.ensure_collection()

print(f"✅ Database models initialized")
