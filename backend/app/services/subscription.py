"""
Subscription service for the Lean Six Sigma RAG Chatbot.

This module provides functionality for:
- Managing subscription plans
- Processing user subscriptions
- Handling payment integrations
- Subscription status updates
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.subscription import (
    SubscriptionPlan, 
    UserSubscription, 
    SubscriptionStatus,
    SubscriptionTier,
    BillingPeriod
)
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    UserSubscriptionCreate,
    UserSubscriptionUpdate,
    PaymentIntentCreate
)

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing subscription plans and user subscriptions"""
    
    @staticmethod
    def create_default_plans(db: Session) -> None:
        """Create default subscription plans if they don't exist"""
        # Check if plans already exist
        existing_plans = db.query(SubscriptionPlan).all()
        if existing_plans:
            return
        
        # Define default plans
        default_plans = [
            {
                "name": "Free",
                "tier": SubscriptionTier.FREE,
                "description": "Basic access with limited queries",
                "price_monthly": 0,
                "price_yearly": 0,
                "daily_query_limit": 10,
                "monthly_query_limit": 100,
                "max_context_docs": 3,
                "has_priority_support": False,
                "has_custom_templates": False,
                "has_team_features": False,
                "has_api_access": False
            },
            {
                "name": "Basic",
                "tier": SubscriptionTier.BASIC,
                "description": "Enhanced access with more queries and features",
                "price_monthly": 9.99,
                "price_yearly": 99.99,
                "daily_query_limit": 50,
                "monthly_query_limit": 1000,
                "max_context_docs": 5,
                "has_priority_support": False,
                "has_custom_templates": True,
                "has_team_features": False,
                "has_api_access": False
            },
            {
                "name": "Professional",
                "tier": SubscriptionTier.PROFESSIONAL,
                "description": "Professional access with advanced features",
                "price_monthly": 19.99,
                "price_yearly": 199.99,
                "daily_query_limit": 200,
                "monthly_query_limit": 5000,
                "max_context_docs": 10,
                "has_priority_support": True,
                "has_custom_templates": True,
                "has_team_features": False,
                "has_api_access": True
            },
            {
                "name": "Enterprise",
                "tier": SubscriptionTier.ENTERPRISE,
                "description": "Full access with team features and unlimited queries",
                "price_monthly": 49.99,
                "price_yearly": 499.99,
                "daily_query_limit": 1000,
                "monthly_query_limit": 30000,
                "max_context_docs": 20,
                "has_priority_support": True,
                "has_custom_templates": True,
                "has_team_features": True,
                "has_api_access": True
            }
        ]
        
        # Create plans
        for plan_data in default_plans:
            plan = SubscriptionPlan(**plan_data)
            db.add(plan)
        
        db.commit()
        logger.info("Created default subscription plans")
    
    @staticmethod
    def get_plans(db: Session) -> List[SubscriptionPlan]:
        """Get all subscription plans"""
        return db.query(SubscriptionPlan).all()
    
    @staticmethod
    def get_plan_by_id(db: Session, plan_id: int) -> Optional[SubscriptionPlan]:
        """Get a subscription plan by ID"""
        return db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    
    @staticmethod
    def create_plan(db: Session, plan_data: SubscriptionPlanCreate) -> SubscriptionPlan:
        """Create a new subscription plan"""
        plan = SubscriptionPlan(**plan_data.dict())
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan
    
    @staticmethod
    def update_plan(
        db: Session, 
        plan_id: int, 
        plan_data: SubscriptionPlanUpdate
    ) -> Optional[SubscriptionPlan]:
        """Update an existing subscription plan"""
        plan = SubscriptionService.get_plan_by_id(db, plan_id)
        if not plan:
            return None
        
        update_data = plan_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(plan, key, value)
        
        db.commit()
        db.refresh(plan)
        return plan
    
    @staticmethod
    def delete_plan(db: Session, plan_id: int) -> bool:
        """Delete a subscription plan"""
        plan = SubscriptionService.get_plan_by_id(db, plan_id)
        if not plan:
            return False
        
        # Check if plan has active subscriptions
        active_subscriptions = db.query(UserSubscription).filter(
            UserSubscription.plan_id == plan_id,
            UserSubscription.status == SubscriptionStatus.ACTIVE
        ).count()
        
        if active_subscriptions > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete plan with {active_subscriptions} active subscriptions"
            )
        
        db.delete(plan)
        db.commit()
        return True
    
    @staticmethod
    def get_user_subscription(db: Session, user_id: int) -> Optional[UserSubscription]:
        """Get the active subscription for a user"""
        return db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status == SubscriptionStatus.ACTIVE
        ).first()
    
    @staticmethod
    def get_user_subscriptions(db: Session, user_id: int) -> List[UserSubscription]:
        """Get all subscriptions for a user"""
        return db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id
        ).all()
    
    @staticmethod
    def create_subscription(
        db: Session, 
        subscription_data: UserSubscriptionCreate
    ) -> UserSubscription:
        """Create a new user subscription"""
        # Check if plan exists
        plan = SubscriptionService.get_plan_by_id(db, subscription_data.plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription plan with ID {subscription_data.plan_id} not found"
            )
        
        # Check if user has an active subscription
        active_subscription = SubscriptionService.get_user_subscription(
            db, subscription_data.user_id
        )
        
        if active_subscription:
            # Cancel the current subscription
            active_subscription.status = SubscriptionStatus.CANCELED
            active_subscription.canceled_at = datetime.utcnow()
            db.commit()
        
        # Calculate end date based on billing period
        start_date = subscription_data.start_date or datetime.utcnow()
        end_date = None
        
        if subscription_data.billing_period == BillingPeriod.MONTHLY:
            end_date = start_date + timedelta(days=30)
        elif subscription_data.billing_period == BillingPeriod.YEARLY:
            end_date = start_date + timedelta(days=365)
        
        # Create new subscription
        subscription_dict = subscription_data.dict()
        subscription_dict["end_date"] = end_date
        
        subscription = UserSubscription(**subscription_dict)
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    def update_subscription(
        db: Session,
        subscription_id: int,
        update_data: UserSubscriptionUpdate
    ) -> Optional[UserSubscription]:
        """Update a user subscription"""
        subscription = db.query(UserSubscription).filter(
            UserSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            return None
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(subscription, key, value)
        
        # If status is changed to canceled, set canceled_at
        if update_data.status == SubscriptionStatus.CANCELED and not subscription.canceled_at:
            subscription.canceled_at = datetime.utcnow()
        
        db.commit()
        db.refresh(subscription)
        return subscription
    
    @staticmethod
    def cancel_subscription(db: Session, subscription_id: int) -> Optional[UserSubscription]:
        """Cancel a user subscription"""
        return SubscriptionService.update_subscription(
            db,
            subscription_id,
            UserSubscriptionUpdate(
                status=SubscriptionStatus.CANCELED,
                canceled_at=datetime.utcnow()
            )
        )
    
    @staticmethod
    def assign_free_plan(db: Session, user: User) -> UserSubscription:
        """Assign the free plan to a new user"""
        # Get the free plan
        free_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == SubscriptionTier.FREE
        ).first()
        
        if not free_plan:
            # Create default plans if they don't exist
            SubscriptionService.create_default_plans(db)
            free_plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.tier == SubscriptionTier.FREE
            ).first()
        
        # Create subscription
        subscription = UserSubscription(
            user_id=user.id,
            plan_id=free_plan.id,
            status=SubscriptionStatus.ACTIVE,
            billing_period=BillingPeriod.LIFETIME,
            start_date=datetime.utcnow()
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    def create_payment_intent(
        db: Session,
        user_id: int,
        payment_data: PaymentIntentCreate
    ) -> Dict[str, Any]:
        """
        Create a payment intent for subscription purchase.
        This is a placeholder for integration with a payment processor like Stripe.
        """
        # Get the plan
        plan = SubscriptionService.get_plan_by_id(db, payment_data.plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription plan with ID {payment_data.plan_id} not found"
            )
        
        # Determine amount based on billing period
        amount = plan.price_monthly
        if payment_data.billing_period == BillingPeriod.YEARLY:
            amount = plan.price_yearly
        
        # This would be replaced with actual payment processor integration
        # For now, return a mock response
        return {
            "client_secret": f"mock_secret_{user_id}_{plan.id}_{datetime.utcnow().timestamp()}",
            "payment_intent_id": f"mock_intent_{user_id}_{plan.id}_{datetime.utcnow().timestamp()}"
        }
    
    @staticmethod
    def process_payment_webhook(db: Session, webhook_data: Dict[str, Any]) -> bool:
        """
        Process payment webhook from payment processor.
        This is a placeholder for integration with a payment processor like Stripe.
        """
        # This would be replaced with actual payment processor integration
        # For now, return success
        return True 