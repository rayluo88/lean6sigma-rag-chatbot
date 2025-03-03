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

from app.models.user import User
from app.models.subscription import UserSubscription, SubscriptionStatus


# Constants for free tier limitations
FREE_TIER_DAILY_LIMIT = 10
FREE_TIER_MONTHLY_LIMIT = 100


def get_user_subscription(user: User, db: Session):
    """
    Get the active subscription for a user.
    Returns None if no active subscription is found.
    """
    if not user.subscriptions:
        return None
    
    # Get the most recent active subscription
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user.id,
        UserSubscription.status == SubscriptionStatus.ACTIVE
    ).order_by(desc(UserSubscription.created_at)).first()
    
    return subscription


def get_user_limits(user: User, db: Session):
    """
    Get the query limits for a user based on their subscription.
    """
    subscription = get_user_subscription(user, db)
    
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


def check_user_limits(user: User, db: Session) -> None:
    """
    Check if a user has exceeded their query limits.
    Raises HTTPException if limits are exceeded.
    """
    # Get user limits based on subscription
    limits = get_user_limits(user, db)
    
    # Reset counters if it's a new day
    if user.last_query_time:
        last_query_date = user.last_query_time.date()
        today = datetime.utcnow().date()
        
        if last_query_date < today:
            user.queries_count = 0
    
    # Check daily limit
    if user.queries_count >= limits["daily_limit"]:
        subscription = get_user_subscription(user, db)
        
        if subscription:
            plan_name = subscription.plan.name
            message = f"Daily limit of {limits['daily_limit']} queries for your {plan_name} plan has been reached."
        else:
            message = f"Free tier daily limit of {FREE_TIER_DAILY_LIMIT} queries exceeded. Please upgrade your plan."
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message
        )


def increment_user_query_count(user: User, db: Session) -> None:
    """
    Increment the user's query count and update last query time.
    """
    user.queries_count += 1
    user.last_query_time = datetime.utcnow()
    db.commit()


def get_remaining_queries(user: User, db: Session) -> dict:
    """
    Get the number of remaining queries for the user.
    """
    limits = get_user_limits(user, db)
    daily_remaining = max(0, limits["daily_limit"] - user.queries_count)
    
    subscription = get_user_subscription(user, db)
    plan_name = "Free" if not subscription else subscription.plan.name
    
    return {
        "daily_queries_remaining": daily_remaining,
        "daily_queries_limit": limits["daily_limit"],
        "plan_name": plan_name,
        "last_query_time": user.last_query_time
    } 