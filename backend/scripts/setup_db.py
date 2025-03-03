"""
Database setup script for Lean Six Sigma RAG Chatbot.
This script:
1. Creates all database tables
2. Adds test user accounts
3. Verifies the setup
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.models.user import User
from app.core.security import get_password_hash

# Import all models to ensure they're registered with Base
from app.models.chat_history import ChatHistory

def setup_database():
    """Create tables and add test users"""
    # Convert PostgresDsn to string
    database_url = str(settings.DATABASE_URL)
    print(f"Connecting to database: {database_url}")
    
    # Create engine and tables
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if test users already exist
        test_user = db.query(User).filter(User.email == "testuser@example.com").first()
        
        if not test_user:
            # Create test users
            test_users = [
                User(
                    email="testuser@example.com",
                    hashed_password=get_password_hash("testpassword"),
                    full_name="Test User",
                    is_active=True
                ),
                User(
                    email="chattest@example.com",
                    hashed_password=get_password_hash("testpassword"),
                    full_name="Chat Test User",
                    is_active=True
                )
            ]
            
            # Add users to database
            for user in test_users:
                db.add(user)
            
            # Commit changes
            db.commit()
            print("Test users created successfully")
        else:
            print("Test users already exist")
        
        # Verify users were created
        users = db.query(User).all()
        print(f"Total users in database: {len(users)}")
        for user in users:
            print(f"- {user.email} ({user.full_name})")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_database() 