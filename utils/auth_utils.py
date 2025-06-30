"""
Authentication utilities
Helper functions for user authentication and session management
"""

from typing import Optional
from passlib.context import CryptContext
from config.auth import auth_manager

# Initialize password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    """Authenticate user with username and password"""
    from models.user import User
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_user_session(user, remember_me: bool = False):
    """Create user session and return session token"""
    from config.auth import session_manager
    from datetime import datetime
    
    # Update last login
    user.update_last_login()
    
    # Create session
    token = session_manager.create_session(
        user_id=user.id,
        username=user.username,
        role=user.role
    )
    
    return token

def validate_session(token: str) -> Optional[dict]:
    """Validate session token and return user info"""
    from config.auth import session_manager
    return session_manager.validate_session(token)

def require_role(required_role: str):
    """Decorator to require specific role for access"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would integrate with Shiny's session management
            # For now, it's a placeholder
            return func(*args, **kwargs)
        return wrapper
    return decorator

def has_permission(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission"""
    from config.auth import has_permission as auth_has_permission
    return auth_has_permission(user_role, required_permission)

def logout_user(token: str) -> bool:
    """Logout user and destroy session"""
    from config.auth import session_manager
    return session_manager.destroy_session(token)

def change_password(db, user_id: int, old_password: str, new_password: str) -> bool:
    """Change user password with verification"""
    from models.user import User
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    # Verify old password
    if not verify_password(old_password, user.hashed_password):
        return False
    
    # Set new password
    user.set_password(new_password)
    db.commit()
    
    return True

def reset_password(db, username: str, new_password: str) -> bool:
    """Reset user password (admin function)"""
    from models.user import User
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    user.set_password(new_password)
    db.commit()
    
    return True
