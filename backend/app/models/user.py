"""
User model for the Lean Six Sigma RAG Chatbot.

This module defines the User database model which handles:
- User authentication information
- Profile details
- Usage tracking for free tier limitations
- Timestamps for user activity
- Relationship with chat history

The model includes features for:
- Email-based authentication
- Role-based access control (superuser flag)
- Query usage tracking
- Account status management
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Free tier tracking
    queries_count = Column(Integer, default=0)
    last_query_time = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>" 