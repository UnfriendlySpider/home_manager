"""
Home Manager Application Configuration
Central configuration management for the entire application
"""

import os
from pathlib import Path
from typing import Optional

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = DATA_DIR / "uploads"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUPS_DIR = DATA_DIR / "backups"

# Ensure directories exist
for directory in [DATA_DIR, UPLOADS_DIR, EXPORTS_DIR, BACKUPS_DIR]:
    directory.mkdir(exist_ok=True)

class Settings:
    """Application settings and configuration"""
    
    # Application settings
    APP_NAME = "Home Manager"
    APP_VERSION = "2.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/home_manager.db")
    DATABASE_ECHO = DEBUG  # Log SQL queries in debug mode
    
    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    ALGORITHM = "HS256"
    
    # File upload settings
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".txt", ".doc", ".docx", ".xlsx", ".csv"}
    
    # Email settings
    SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@homemanager.local")
    
    # Pagination settings
    DEFAULT_PAGE_SIZE = 25
    MAX_PAGE_SIZE = 100
    
    # Dashboard settings
    DASHBOARD_REFRESH_INTERVAL = 30  # seconds
    CHART_COLOR_PALETTE = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]
    
    # Notification settings
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "False").lower() == "true"
    NOTIFICATION_BATCH_SIZE = 50
    
    # Backup settings
    AUTO_BACKUP_ENABLED = True
    BACKUP_RETENTION_DAYS = 30
    BACKUP_SCHEDULE_HOUR = 2  # 2 AM daily backup
    
    # Session settings
    SESSION_TIMEOUT_MINUTES = 60
    REMEMBER_ME_DAYS = 30

# Application constants
class Constants:
    """Application-wide constants"""
    
    # User roles
    ROLE_ADMIN = "admin"
    ROLE_FAMILY_MEMBER = "family_member"
    ROLE_GUEST = "guest"
    
    USER_ROLES = [ROLE_ADMIN, ROLE_FAMILY_MEMBER, ROLE_GUEST]
    
    # Task priorities
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"
    
    TASK_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_URGENT]
    
    # Task statuses
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    
    TASK_STATUSES = [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_CANCELLED]
    
    # Expense categories
    EXPENSE_CATEGORIES = [
        "Utilities",
        "Maintenance",
        "Improvements",
        "Insurance",
        "Property Tax",
        "Mortgage",
        "Supplies",
        "Services",
        "Emergency Repairs",
        "Other"
    ]
    
    # Inventory categories
    INVENTORY_CATEGORIES = [
        "Kitchen",
        "Bathroom",
        "Living Room",
        "Bedroom",
        "Garage",
        "Basement",
        "Attic",
        "Office",
        "Outdoor",
        "Storage",
        "Other"
    ]
    
    # Maintenance categories
    MAINTENANCE_CATEGORIES = [
        "HVAC",
        "Plumbing",
        "Electrical",
        "Roofing",
        "Flooring",
        "Appliances",
        "Exterior",
        "Interior",
        "Landscaping",
        "Security",
        "Other"
    ]
    
    # Document categories
    DOCUMENT_CATEGORIES = [
        "Insurance",
        "Warranties",
        "Manuals",
        "Receipts",
        "Contracts",
        "Legal",
        "Tax Documents",
        "Maintenance Records",
        "Invoices",
        "Other"
    ]
    
    # Recurring frequencies
    FREQUENCY_DAILY = "daily"
    FREQUENCY_WEEKLY = "weekly"
    FREQUENCY_MONTHLY = "monthly"
    FREQUENCY_QUARTERLY = "quarterly"
    FREQUENCY_YEARLY = "yearly"
    
    RECURRING_FREQUENCIES = [
        FREQUENCY_DAILY,
        FREQUENCY_WEEKLY,
        FREQUENCY_MONTHLY,
        FREQUENCY_QUARTERLY,
        FREQUENCY_YEARLY
    ]

# Create global settings instance
settings = Settings()
constants = Constants()
