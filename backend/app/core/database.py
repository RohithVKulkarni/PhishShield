"""
Database Configuration and Session Management

This module sets up SQLAlchemy for PhishShield's database operations.
Currently configured for SQLite, but can be easily switched to PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
# SQLite: creates file-based database
# For PostgreSQL: use settings.SQLALCHEMY_DATABASE_URI with postgres://...
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False} if "sqlite" in settings.SQLALCHEMY_DATABASE_URI else {},
    echo=False  # Set to True for SQL query logging during development
)

# Session factory for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI endpoints.
    
    Provides a database session that automatically closes after use.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    
    Creates all tables defined in models.py if they don't exist.
    Called on application startup.
    """
    from app.core.models import Base  # Import here to avoid circular imports
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables initialized")
