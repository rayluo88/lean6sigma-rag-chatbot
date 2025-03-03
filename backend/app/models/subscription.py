"""
Subscription models for the Lean Six Sigma RAG Chatbot.

This module defines:
- SubscriptionPlan: Different subscription tiers available
- UserSubscription: User's subscription status and history
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class SubscriptionTier(str, enum.Enum):
    """Enum for subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionPlan(Base):
    """Subscription plan model defining available tiers"""
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tier = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price_monthly = Column(Float, nullable=False)
    price_yearly = Column(Float, nullable=False)
    
    # Plan limits
    daily_query_limit = Column(Integer, nullable=False)
    monthly_query_limit = Column(Integer, nullable=False)
    max_context_docs = Column(Integer, nullable=False)
    has_priority_support = Column(Boolean, default=False)
    has_custom_templates = Column(Boolean, default=False)
    has_team_features = Column(Boolean, default=False)
    has_api_access = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")
    
    def __repr__(self):
        return f"<SubscriptionPlan {self.name}>"


class SubscriptionStatus(str, enum.Enum):
    """Enum for subscription status"""
    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PENDING = "pending"
    TRIAL = "trial"


class BillingPeriod(str, enum.Enum):
    """Enum for billing period"""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class UserSubscription(Base):
    """User subscription model tracking subscription status"""
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    
    # Subscription details
    status = Column(String, default=SubscriptionStatus.ACTIVE, nullable=False)
    billing_period = Column(String, default=BillingPeriod.MONTHLY, nullable=False)
    
    # Payment tracking
    payment_provider = Column(String, nullable=True)
    payment_id = Column(String, nullable=True)
    
    # Dates
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)
    trial_end_date = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<UserSubscription {self.user_id}:{self.plan_id}>" 