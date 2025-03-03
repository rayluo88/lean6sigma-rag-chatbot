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
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token

# Import the subscription service
from app.services.subscription import SubscriptionService

router = APIRouter()

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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
    
    # Assign the free plan to the new user
    try:
        SubscriptionService.assign_free_plan(db, new_user)
        logger.info("Free plan assigned to new user: %s", new_user.email)
    except Exception as e:
        logger.error("Failed to assign free plan to user %s: %s", new_user.email, str(e))
    
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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current admin user.
    Raises an exception if the user is not an admin.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    return current_user 