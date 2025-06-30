"""
Base database model with common fields and functionality
Provides shared functionality for all models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declared_attr
from config.database import Base

class BaseModel(Base):
    """Base model with common fields for all tables"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name"""
        return cls.__name__.lower()
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: dict):
        """Update model instance from dictionary"""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

class TimestampMixin:
    """Mixin for models that need created/updated timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SoftDeleteMixin:
    """Mixin for models that support soft deletion"""
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(String, default=False, nullable=False)
    
    def soft_delete(self):
        """Mark record as deleted without removing from database"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft-deleted record"""
        self.is_deleted = False
        self.deleted_at = None
