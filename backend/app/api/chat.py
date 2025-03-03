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
from typing import List
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


class ChatResponse(BaseModel):
    response: str
    remaining_queries: dict
    history_id: int


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
    """Get the number of queries remaining for the current user."""
    return get_remaining_queries(current_user, db)


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a user query through the RAG-based chatbot:
    1. Check user's query limits
    2. Retrieve context from the Lean Six Sigma knowledge base
    3. Generate a response using OpenAI
    4. Store the chat history in the database
    5. Return the generated response and remaining queries
    """
    try:
        # Check if user has exceeded their query limits
        check_user_limits(current_user, db)

        # Log the user query
        logger.info("User %s submitted query: %s", current_user.email, chat_request.query)

        # Generate response using RAG service
        response_text = await rag_service.generate_response(chat_request.query)

        # Save chat history in the database
        chat_history_entry = ChatHistory(
            user_id=current_user.id, 
            query=chat_request.query, 
            response=response_text
        )
        db.add(chat_history_entry)
        db.commit()
        db.refresh(chat_history_entry)
        
        # Increment user's query count
        increment_user_query_count(current_user, db)
        
        # Get remaining queries
        remaining = get_remaining_queries(current_user, db)

        return ChatResponse(
            response=response_text,
            remaining_queries=remaining,
            history_id=chat_history_entry.id
        )
        
    except Exception as e:
        logger.error("Error processing chat request: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your request. Please try again."
        ) 