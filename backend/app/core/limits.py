"""
Query limiting and rate limiting functionality for the Lean Six Sigma RAG Chatbot.

This module provides:
- Free tier query limit checking
- Rate limiting for API endpoints
- Query count tracking
- Limit reset scheduling
"""

from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User


# Constants for free tier limitations
FREE_TIER_DAILY_LIMIT = 10
FREE_TIER_MONTHLY_LIMIT = 100


def check_user_limits(user: User, db: Session) -> None:
    """
    Check if a user has exceeded their query limits.
    Raises HTTPException if limits are exceeded.
    """
    # Reset counters if it's a new day
    if user.last_query_time:
        last_query_date = user.last_query_time.date()
        today = datetime.utcnow().date()
        
        if last_query_date < today:
            user.queries_count = 0
    
    # Check daily limit
    if user.queries_count >= FREE_TIER_DAILY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Free tier daily limit of {FREE_TIER_DAILY_LIMIT} queries exceeded. Please try again tomorrow or upgrade your plan."
        )


def increment_user_query_count(user: User, db: Session) -> None:
    """
    Increment the user's query count and update last query time.
    """
    user.queries_count += 1
    user.last_query_time = datetime.utcnow()
    db.commit()


def get_remaining_queries(user: User) -> dict:
    """
    Get the number of remaining queries for the user.
    """
    daily_remaining = max(0, FREE_TIER_DAILY_LIMIT - user.queries_count)
    
    return {
        "daily_queries_remaining": daily_remaining,
        "daily_queries_limit": FREE_TIER_DAILY_LIMIT,
        "last_query_time": user.last_query_time
    } 