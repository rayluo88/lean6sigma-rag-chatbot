"""
Authentication API endpoints for Lean Six Sigma RAG Chatbot.

This module provides endpoints for:
- User registration (/register)
- User login (/login)

Endpoints:
  POST /register: Accepts new user details, creates a new user after hashing the password, and returns the user data.
  POST /login: Accepts user login credentials, verifies the credentials, and returns a JWT access token.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Endpoint for user registration. Creates a new user after verifying that the email is not already in use."""
    # Check if the user already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        logger.warning("Registration attempt with already registered email: %s", user_in.email)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Hash the provided password
    hashed_password = get_password_hash(user_in.password)
    
    # Create a new user instance
    new_user = User(email=user_in.email, full_name=user_in.full_name, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info("User registered successfully: %s", new_user.email)
    return new_user


@router.post("/login", response_model=Token)
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    """Endpoint for user login. Verifies credentials and returns an access token if successful."""
    # Retrieve the user by email
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        logger.warning("Failed login attempt for email: %s", user_in.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Set the token expiry time
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    logger.info("User logged in successfully: %s", user.email)
    return Token(access_token=token, token_type="bearer") 