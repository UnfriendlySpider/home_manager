"""
Database configuration and connection management
Handles SQLAlchemy setup and database operations
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
            "timeout": 20,
        },
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
        cursor.close()
        
else:
    # PostgreSQL or other database configuration
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()

def get_database() -> Generator[Session, None, None]:
    """
    Database dependency that yields a database session.
    Automatically handles session cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    try:
        # Import all models to ensure they are registered
        from models import user, maintenance, inventory, financial, tasks, documents
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create default admin user if it doesn't exist
        _create_default_admin()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def _create_default_admin():
    """Create default admin user if no users exist"""
    try:
        from models.user import User
        from utils.auth_utils import get_password_hash
        
        db = SessionLocal()
        
        # Check if any users exist
        existing_users = db.query(User).first()
        if not existing_users:
            # Create default admin user
            default_admin = User(
                username="admin",
                email="admin@homemanager.local",
                full_name="Administrator",
                hashed_password=get_password_hash("admin123"),  # Change this in production!
                role="admin",
                is_active=True
            )
            db.add(default_admin)
            db.commit()
            logger.info("Default admin user created (username: admin, password: admin123)")
            logger.warning("IMPORTANT: Change the default admin password in production!")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Failed to create default admin user: {e}")

def drop_all_tables():
    """
    Drop all database tables.
    WARNING: This will delete all data!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise

def backup_database(backup_path: str = None):
    """
    Create a backup of the database.
    Currently supports SQLite databases.
    """
    if not settings.DATABASE_URL.startswith("sqlite"):
        logger.warning("Database backup currently only supports SQLite")
        return False
    
    try:
        import shutil
        from datetime import datetime
        from config.settings import BACKUPS_DIR
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = BACKUPS_DIR / f"backup_{timestamp}.db"
        
        # Extract database file path from URL
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backup created: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to backup database: {e}")
        return False

def restore_database(backup_path: str):
    """
    Restore database from backup.
    Currently supports SQLite databases.
    """
    if not settings.DATABASE_URL.startswith("sqlite"):
        logger.warning("Database restore currently only supports SQLite")
        return False
    
    try:
        import shutil
        from pathlib import Path
        
        if not Path(backup_path).exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Extract database file path from URL
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        
        # Close all connections
        engine.dispose()
        
        # Restore database file
        shutil.copy2(backup_path, db_path)
        logger.info(f"Database restored from: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to restore database: {e}")
        return False

# Health check function
def check_database_health() -> bool:
    """Check if database is accessible and responsive"""
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
