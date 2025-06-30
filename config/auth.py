"""
Authentication configuration and utilities
Handles user authentication, session management, and security
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import jwt
from passlib.context import CryptContext
from config.settings import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    """Centralized authentication management"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    def create_session_token(self, user_id: int, username: str, role: str) -> str:
        """Create session token for user"""
        token_data = {
            "sub": str(user_id),
            "username": username,
            "role": role,
            "iat": datetime.utcnow()
        }
        return self.create_access_token(token_data)
    
    def validate_session_token(self, token: str) -> Optional[dict]:
        """Validate session token and return user data"""
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp is None:
            return None
        
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        return {
            "user_id": int(payload.get("sub")),
            "username": payload.get("username"),
            "role": payload.get("role")
        }

# Global auth manager instance
auth_manager = AuthManager()

class SessionManager:
    """Manage user sessions and authentication state"""
    
    def __init__(self):
        self.active_sessions = {}  # In-memory session storage
    
    def create_session(self, user_id: int, username: str, role: str) -> str:
        """Create new user session"""
        token = auth_manager.create_session_token(user_id, username, role)
        
        session_data = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "token": token
        }
        
        self.active_sessions[token] = session_data
        return token
    
    def validate_session(self, token: str) -> Optional[dict]:
        """Validate session and update last activity"""
        if token not in self.active_sessions:
            return None
        
        session_data = self.active_sessions[token]
        
        # Check if session has expired
        last_activity = session_data["last_activity"]
        timeout = timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
        
        if datetime.utcnow() - last_activity > timeout:
            self.destroy_session(token)
            return None
        
        # Update last activity
        session_data["last_activity"] = datetime.utcnow()
        
        return {
            "user_id": session_data["user_id"],
            "username": session_data["username"],
            "role": session_data["role"]
        }
    
    def destroy_session(self, token: str) -> bool:
        """Destroy user session"""
        if token in self.active_sessions:
            del self.active_sessions[token]
            return True
        return False
    
    def get_user_sessions(self, user_id: int) -> list:
        """Get all active sessions for a user"""
        user_sessions = []
        for token, session_data in self.active_sessions.items():
            if session_data["user_id"] == user_id:
                user_sessions.append({
                    "token": token,
                    "created_at": session_data["created_at"],
                    "last_activity": session_data["last_activity"]
                })
        return user_sessions
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        timeout = timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
        current_time = datetime.utcnow()
        
        expired_tokens = []
        for token, session_data in self.active_sessions.items():
            if current_time - session_data["last_activity"] > timeout:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self.active_sessions[token]
        
        return len(expired_tokens)

# Global session manager instance
session_manager = SessionManager()

def require_auth(role: Optional[str] = None):
    """Decorator to require authentication for functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be implemented with Shiny's session management
            # For now, this is a placeholder for the authentication requirement
            return func(*args, **kwargs)
        return wrapper
    return decorator

def has_permission(user_role: str, required_role: str) -> bool:
    """Check if user has required permission level"""
    role_hierarchy = {
        "guest": 0,
        "family_member": 1,
        "admin": 2
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level
