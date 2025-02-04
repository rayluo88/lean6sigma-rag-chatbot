"""
Chat history model for the Lean Six Sigma RAG Chatbot.

This module defines the ChatHistory database model which stores:
- User chat interactions
- RAG-generated responses
- Token usage tracking
- Context documents used in responses

Features:
- Links to user accounts
- Stores full conversation context
- Tracks token usage for billing/limits
- Maintains metadata about RAG context
- Timestamps for analytics
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    
    # Metadata
    tokens_used = Column(Integer, default=0)
    context_docs = Column(Text, nullable=True)  # JSON string of used documents
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_history")
    
    def __repr__(self):
        return f"<ChatHistory {self.id}>" 