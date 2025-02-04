"""
Database configuration and session management for the Lean Six Sigma RAG Chatbot.

This module provides:
- Database engine configuration
- Session management
- Base class for SQLAlchemy models
- Database connection pooling setup
- Database dependency injection for FastAPI

The database connection is configured using SQLAlchemy with connection pooling
for optimal performance and resource management.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

from app.core.config import settings

engine = create_engine(
    str(settings.DATABASE_URL),
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 