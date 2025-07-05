"""
User Authentication and Management Routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
import jwt
from datetime import datetime, timedelta, timezone
import os
from database.models import user_model, chat_history_model, learning_session_model

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    skill_level: Optional[str] = "beginner"
    preferences: Optional[Dict] = {}

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    skill_level: str
    completed_topics: List[str]
    known_concepts: List[str]
    is_active: bool
    created_at: datetime
    statistics: Dict

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_key_here")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(user_id: str = Depends(verify_token)):
    """Get current authenticated user"""
    user = user_model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/register", response_model=Token)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = user_model.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user_dict = user_data.dict()
    user_id = user_model.create_user(user_dict)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Get created user
    user = user_model.get_user_by_id(user_id)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id})
    
    user_response = UserResponse(
        id=user["_id"],
        email=user["email"],
        full_name=user["full_name"],
        skill_level=user["skill_level"],
        completed_topics=user["completed_topics"],
        known_concepts=user["known_concepts"],
        is_active=user["is_active"],
        created_at=user["created_at"],
        statistics=user["statistics"]
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin):
    """Login user"""
    # Get user by email
    user = user_model.get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not user_model.verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["_id"]})
    
    user_response = UserResponse(
        id=user["_id"],
        email=user["email"],
        full_name=user["full_name"],
        skill_level=user["skill_level"],
        completed_topics=user["completed_topics"],
        known_concepts=user["known_concepts"],
        is_active=user["is_active"],
        created_at=user["created_at"],
        statistics=user["statistics"]
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user["_id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        skill_level=current_user["skill_level"],
        completed_topics=current_user["completed_topics"],
        known_concepts=current_user["known_concepts"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        statistics=current_user["statistics"]
    )

@router.get("/chat-history")
async def get_user_chat_history(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """Get user's chat history"""
    chat_history = chat_history_model.get_chat_history(current_user["_id"], limit)
    return {"chat_history": chat_history}

@router.put("/update-progress")
async def update_user_progress(
    completed_topic: Optional[str] = None,
    known_concepts: Optional[List[str]] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Update user's learning progress"""
    success = user_model.update_user_progress(
        current_user["_id"],
        completed_topic,
        known_concepts
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update progress"
        )
    
    # Get updated user data
    updated_user = user_model.get_user_by_id(current_user["_id"])
    return {
        "message": "Progress updated successfully",
        "completed_topics": updated_user["completed_topics"],
        "known_concepts": updated_user["known_concepts"],
        "statistics": updated_user["statistics"]
    }
