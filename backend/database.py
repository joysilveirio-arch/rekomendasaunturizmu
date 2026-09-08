"""
Database Configuration and Session Management
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from backend.config import settings


# ============================================================
# DATABASE ENGINE
# ============================================================

DATABASE_URL = settings.get_database_url()

connect_args = {}

if "sqlite" in DATABASE_URL:
    connect_args = {
        "check_same_thread": False
    }

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)


# ============================================================
# SESSION FACTORY
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# BASE CLASS
# ============================================================

Base = declarative_base()


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    """
    Initialize database and create all tables.

    All models must be imported before create_all()
    so SQLAlchemy knows all tables.
    """

    # Import all models
    from backend.models.destination import Destination
    from backend.models.review import Review
    from backend.models.recommendation import Recommendation

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("Database tables initialized successfully.")


# ============================================================
# DROP DATABASE TABLES
# ============================================================

def drop_db():
    """
    Drop all tables.
    WARNING: This will delete database structure/data.
    """

    Base.metadata.drop_all(bind=engine)

    print("All database tables dropped.")