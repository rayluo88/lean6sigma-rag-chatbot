"""
Subscription schemas for the Lean Six Sigma RAG Chatbot.

This module defines Pydantic models for:
- Subscription plans
- User subscriptions
- Subscription status updates
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class SubscriptionTierEnum(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatusEnum(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PENDING = "pending"
    TRIAL = "trial"


class BillingPeriodEnum(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


# Subscription Plan Schemas
class SubscriptionPlanBase(BaseModel):
    name: str
    tier: SubscriptionTierEnum
    description: str
    price_monthly: float
    price_yearly: float
    daily_query_limit: int
    monthly_query_limit: int
    max_context_docs: int
    has_priority_support: bool = False
    has_custom_templates: bool = False
    has_team_features: bool = False
    has_api_access: bool = False


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[float] = None
    price_yearly: Optional[float] = None
    daily_query_limit: Optional[int] = None
    monthly_query_limit: Optional[int] = None
    max_context_docs: Optional[int] = None
    has_priority_support: Optional[bool] = None
    has_custom_templates: Optional[bool] = None
    has_team_features: Optional[bool] = None
    has_api_access: Optional[bool] = None


class SubscriptionPlanOut(SubscriptionPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# User Subscription Schemas
class UserSubscriptionBase(BaseModel):
    plan_id: int
    status: SubscriptionStatusEnum = SubscriptionStatusEnum.ACTIVE
    billing_period: BillingPeriodEnum = BillingPeriodEnum.MONTHLY
    payment_provider: Optional[str] = None
    payment_id: Optional[str] = None
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None


class UserSubscriptionCreate(UserSubscriptionBase):
    user_id: int


class UserSubscriptionUpdate(BaseModel):
    plan_id: Optional[int] = None
    status: Optional[SubscriptionStatusEnum] = None
    billing_period: Optional[BillingPeriodEnum] = None
    payment_provider: Optional[str] = None
    payment_id: Optional[str] = None
    end_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    canceled_at: Optional[datetime] = None


class UserSubscriptionOut(UserSubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    canceled_at: Optional[datetime] = None
    plan: SubscriptionPlanOut

    class Config:
        from_attributes = True


# Payment Schemas
class PaymentIntentCreate(BaseModel):
    plan_id: int
    billing_period: BillingPeriodEnum


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str


# Subscription Status Update
class SubscriptionStatusUpdate(BaseModel):
    status: SubscriptionStatusEnum 