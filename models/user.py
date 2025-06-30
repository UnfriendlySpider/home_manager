"""
User model for authentication and user management
Handles user accounts, roles, and profile information
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from models.base import BaseModel

class User(BaseModel):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    # Authentication fields
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile fields
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="family_member")  # admin, family_member, guest
    
    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Profile information
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Preferences
    timezone = Column(String(50), default="UTC", nullable=False)
    date_format = Column(String(20), default="%Y-%m-%d", nullable=False)
    theme = Column(String(20), default="light", nullable=False)  # light, dark
    language = Column(String(10), default="en", nullable=False)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    task_reminders = Column(Boolean, default=True, nullable=False)
    maintenance_alerts = Column(Boolean, default=True, nullable=False)
    budget_alerts = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches user's password"""
        from config.auth import auth_manager
        return auth_manager.verify_password(password, self.hashed_password)
    
    def set_password(self, password: str):
        """Set user's password with proper hashing"""
        from config.auth import auth_manager
        self.hashed_password = auth_manager.get_password_hash(password)
    
    def update_last_login(self):
        """Update user's last login timestamp"""
        self.last_login = datetime.utcnow()
    
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == "admin"
    
    def is_family_member(self) -> bool:
        """Check if user is a family member or admin"""
        return self.role in ["admin", "family_member"]
    
    def can_access_feature(self, feature: str) -> bool:
        """Check if user can access a specific feature based on role"""
        # Admin can access everything
        if self.role == "admin":
            return True
        
        # Family members can access most features
        if self.role == "family_member":
            restricted_features = ["user_management", "system_settings"]
            return feature not in restricted_features
        
        # Guests have limited access
        if self.role == "guest":
            allowed_features = ["dashboard", "view_tasks", "view_inventory"]
            return feature in allowed_features
        
        return False
    
    def get_profile_dict(self) -> dict:
        """Get user profile information as dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "avatar_url": self.avatar_url,
            "phone": self.phone,
            "bio": self.bio,
            "timezone": self.timezone,
            "theme": self.theme,
            "language": self.language,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat()
        }
    
    def get_preferences_dict(self) -> dict:
        """Get user preferences as dictionary"""
        return {
            "timezone": self.timezone,
            "date_format": self.date_format,
            "theme": self.theme,
            "language": self.language,
            "email_notifications": self.email_notifications,
            "task_reminders": self.task_reminders,
            "maintenance_alerts": self.maintenance_alerts,
            "budget_alerts": self.budget_alerts
        }
    
    def update_preferences(self, preferences: dict):
        """Update user preferences from dictionary"""
        allowed_fields = [
            "timezone", "date_format", "theme", "language",
            "email_notifications", "task_reminders", 
            "maintenance_alerts", "budget_alerts"
        ]
        
        for field, value in preferences.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        
        self.updated_at = datetime.utcnow()

class UserSession(BaseModel):
    """User session tracking for security and analytics"""
    
    __tablename__ = "user_sessions"
    
    user_id = Column(String, nullable=False, index=True)
    session_token = Column(String(500), nullable=False, unique=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at
    
    def deactivate(self):
        """Deactivate session"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

class UserActivity(BaseModel):
    """Track user activity for analytics and security"""
    
    __tablename__ = "user_activity"
    
    user_id = Column(String, nullable=False, index=True)
    action = Column(String(100), nullable=False)  # login, logout, create_task, etc.
    resource = Column(String(100), nullable=True)  # task, maintenance, etc.
    resource_id = Column(String, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    details = Column(Text, nullable=True)  # JSON string with additional details
    
    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, action='{self.action}')>"
