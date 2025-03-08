'''Chat API endpoints for RAG-based chatbot.

This module provides endpoints for:
- Processing user queries
- Storing chat history
- Retrieving chat history
- Managing query limits
'''

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, constr
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.db.base import get_db
from app.models.chat import ChatHistory
from app.models.user import User
from app.api.auth import get_current_user
from app.core.limits import check_user_limits, increment_user_query_count, get_remaining_queries
from app.services.rag import rag_service

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    query: constr(min_length=1, strip_whitespace=True)


class ChatHistoryResponse(BaseModel):
    id: int
    query: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True


class SourceDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]


class ChatResponse(BaseModel):
    response: str
    remaining_queries: dict
    history_id: int
    sources: Optional[List[SourceDocument]] = []


@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for the current user."""
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.desc()).all()
    return history


@router.get("/remaining", response_model=dict)
def get_remaining_query_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Get remaining query count for the current user."""
    return get_remaining_queries(current_user.id, db)


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a chat request and return a response."""
    try:
        # Check if user has remaining queries
        limits = check_user_limits(current_user.id, db)
        if not limits["can_query"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Query limit reached. Please try again tomorrow or upgrade your plan."
            )
        
        # Get user's chat history for context
        chat_history = []
        history_records = db.query(ChatHistory).filter(
            ChatHistory.user_id == current_user.id
        ).order_by(ChatHistory.created_at.desc()).limit(5).all()
        
        for record in reversed(history_records):
            chat_history.append({"role": "user", "content": record.query})
            chat_history.append({"role": "assistant", "content": record.response})
        
        # Generate response using RAG service
        result = await rag_service.generate_response(chat_request.query, chat_history)
        response_text = result["response"]
        sources = result.get("sources", [])
        
        # Store chat in history
        chat_history_entry = ChatHistory(
            user_id=current_user.id,
            query=chat_request.query,
            response=response_text
        )
        db.add(chat_history_entry)
        db.commit()
        db.refresh(chat_history_entry)
        
        # Increment query count
        increment_user_query_count(current_user.id, db)
        
        # Get updated query limits
        remaining = get_remaining_queries(current_user.id, db)
        
        return ChatResponse(
            response=response_text,
            remaining_queries=remaining,
            history_id=chat_history_entry.id,
            sources=sources
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request."
        ) 