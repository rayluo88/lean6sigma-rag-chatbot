"""
Chat history model for Lean Six Sigma RAG Chatbot.

This module defines the ChatHistory SQLAlchemy model for storing:
- User queries
- System responses
- Timestamps
- User references
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class ChatHistory(Base):
    """Model for storing chat history between users and the chatbot."""
    
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to User model
    user = relationship("User", back_populates="chat_history") 