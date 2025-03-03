"""
API endpoints for subscription management.

This module provides endpoints for:
- Listing subscription plans
- Managing user subscriptions
- Processing payments
- Handling subscription status changes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.api.auth import get_current_user, get_current_admin
from app.services.subscription import SubscriptionService
from app.schemas.subscription import (
    SubscriptionPlanOut,
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    UserSubscriptionOut,
    UserSubscriptionCreate,
    UserSubscriptionUpdate,
    PaymentIntentCreate,
    PaymentIntentResponse,
    SubscriptionStatusUpdate
)

router = APIRouter()


# Public endpoints
@router.get("/plans", response_model=List[SubscriptionPlanOut])
def list_plans(db: Session = Depends(get_db)):
    """List all available subscription plans"""
    return SubscriptionService.get_plans(db)


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanOut)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get details of a specific subscription plan"""
    plan = SubscriptionService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription plan with ID {plan_id} not found"
        )
    return plan


# User subscription endpoints
@router.get("/my", response_model=Optional[UserSubscriptionOut])
def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's active subscription"""
    return SubscriptionService.get_user_subscription(db, current_user.id)


@router.get("/my/history", response_model=List[UserSubscriptionOut])
def get_my_subscription_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's subscription history"""
    return SubscriptionService.get_user_subscriptions(db, current_user.id)


@router.post("/subscribe", response_model=UserSubscriptionOut)
def create_subscription(
    subscription_data: UserSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new subscription for the current user"""
    # Ensure user_id matches current user
    subscription_data.user_id = current_user.id
    
    return SubscriptionService.create_subscription(db, subscription_data)


@router.post("/payment/create", response_model=PaymentIntentResponse)
def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a payment intent for subscription purchase"""
    return SubscriptionService.create_payment_intent(db, current_user.id, payment_data)


@router.post("/my/cancel", response_model=UserSubscriptionOut)
def cancel_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel the current user's active subscription"""
    subscription = SubscriptionService.get_user_subscription(db, current_user.id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return SubscriptionService.cancel_subscription(db, subscription.id)


# Admin endpoints
@router.post("/plans", response_model=SubscriptionPlanOut, dependencies=[Depends(get_current_admin)])
def create_plan(
    plan_data: SubscriptionPlanCreate,
    db: Session = Depends(get_db)
):
    """Create a new subscription plan (admin only)"""
    return SubscriptionService.create_plan(db, plan_data)


@router.put("/plans/{plan_id}", response_model=SubscriptionPlanOut, dependencies=[Depends(get_current_admin)])
def update_plan(
    plan_id: int,
    plan_data: SubscriptionPlanUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing subscription plan (admin only)"""
    plan = SubscriptionService.update_plan(db, plan_id, plan_data)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription plan with ID {plan_id} not found"
        )
    return plan


@router.delete("/plans/{plan_id}", dependencies=[Depends(get_current_admin)])
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    """Delete a subscription plan (admin only)"""
    success = SubscriptionService.delete_plan(db, plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription plan with ID {plan_id} not found"
        )
    return {"message": f"Subscription plan with ID {plan_id} deleted successfully"}


@router.get("/users/{user_id}/subscriptions", response_model=List[UserSubscriptionOut], dependencies=[Depends(get_current_admin)])
def get_user_subscriptions(user_id: int, db: Session = Depends(get_db)):
    """Get all subscriptions for a specific user (admin only)"""
    return SubscriptionService.get_user_subscriptions(db, user_id)


@router.put("/subscriptions/{subscription_id}", response_model=UserSubscriptionOut, dependencies=[Depends(get_current_admin)])
def update_subscription(
    subscription_id: int,
    update_data: UserSubscriptionUpdate,
    db: Session = Depends(get_db)
):
    """Update a user subscription (admin only)"""
    subscription = SubscriptionService.update_subscription(db, subscription_id, update_data)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {subscription_id} not found"
        )
    return subscription


# Webhook endpoint for payment processor
@router.post("/webhook/payment")
async def payment_webhook(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for payment processor callbacks.
    This is a placeholder for integration with a payment processor like Stripe.
    """
    # This would be replaced with actual payment processor integration
    # For now, return success
    return {"status": "success"} 