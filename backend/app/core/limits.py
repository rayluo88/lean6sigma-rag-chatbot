"""
Query limiting and rate limiting functionality for the Lean Six Sigma RAG Chatbot.

This module provides:
- Free tier query limit checking
- Rate limiting for API endpoints
- Query count tracking
- Limit reset scheduling
- Subscription-based limit management
"""

from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, Any, Union

from app.models.user import User
from app.models.subscription import UserSubscription, SubscriptionStatus


# Constants for free tier limitations
FREE_TIER_DAILY_LIMIT = 10
FREE_TIER_MONTHLY_LIMIT = 100


def get_user_subscription(user_id: int, db: Session) -> Union[UserSubscription, None]:
    """
    Get the active subscription for a user.
    Returns None if no active subscription is found.
    
    Args:
        user_id: The user ID
        db: Database session
        
    Returns:
        The active subscription or None
    """
    # Get the most recent active subscription
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.status == SubscriptionStatus.ACTIVE
    ).order_by(desc(UserSubscription.created_at)).first()
    
    return subscription


def get_user_limits(user_id: int, db: Session) -> Dict[str, int]:
    """
    Get the query limits for a user based on their subscription.
    
    Args:
        user_id: The user ID
        db: Database session
        
    Returns:
        Dictionary with limit information
    """
    subscription = get_user_subscription(user_id, db)
    
    if not subscription:
        return {
            "daily_limit": FREE_TIER_DAILY_LIMIT,
            "monthly_limit": FREE_TIER_MONTHLY_LIMIT,
            "max_context_docs": 3
        }
    
    return {
        "daily_limit": subscription.plan.daily_query_limit,
        "monthly_limit": subscription.plan.monthly_query_limit,
        "max_context_docs": subscription.plan.max_context_docs
    }


def check_user_limits(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Check if a user has exceeded their query limits.
    
    Args:
        user_id: The user ID
        db: Database session
        
    Returns:
        Dictionary with limit information and whether the user can query
        
    Raises:
        HTTPException: If the user has exceeded their limits
    """
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user limits
    limits = get_user_limits(user_id, db)
    
    # Check daily limit
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    daily_count = user.daily_query_count or 0
    
    # Check monthly limit
    month_start = datetime(today.year, today.month, 1)
    next_month = today.month + 1 if today.month < 12 else 1
    next_month_year = today.year if today.month < 12 else today.year + 1
    month_end = datetime(next_month_year, next_month, 1) - timedelta(days=1)
    
    monthly_count = user.monthly_query_count or 0
    
    # Determine if user can query
    can_query = (daily_count < limits["daily_limit"]) and (monthly_count < limits["monthly_limit"])
    
    return {
        "can_query": can_query,
        "daily_count": daily_count,
        "monthly_count": monthly_count,
        "daily_limit": limits["daily_limit"],
        "monthly_limit": limits["monthly_limit"]
    }


def increment_user_query_count(user_id: int, db: Session) -> None:
    """
    Increment a user's query count.
    
    Args:
        user_id: The user ID
        db: Database session
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.daily_query_count = (user.daily_query_count or 0) + 1
        user.monthly_query_count = (user.monthly_query_count or 0) + 1
        db.commit()


def get_remaining_queries(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Get the number of queries remaining for a user.
    
    Args:
        user_id: The user ID
        db: Database session
        
    Returns:
        Dictionary with remaining query information
    """
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {
            "daily_remaining": 0,
            "monthly_remaining": 0,
            "daily_limit": FREE_TIER_DAILY_LIMIT,
            "monthly_limit": FREE_TIER_MONTHLY_LIMIT
        }
    
    # Get user limits
    limits = get_user_limits(user_id, db)
    
    # Calculate remaining queries
    daily_count = user.daily_query_count or 0
    monthly_count = user.monthly_query_count or 0
    
    daily_remaining = max(0, limits["daily_limit"] - daily_count)
    monthly_remaining = max(0, limits["monthly_limit"] - monthly_count)
    
    return {
        "daily_remaining": daily_remaining,
        "monthly_remaining": monthly_remaining,
        "daily_limit": limits["daily_limit"],
        "monthly_limit": limits["monthly_limit"]
    } 