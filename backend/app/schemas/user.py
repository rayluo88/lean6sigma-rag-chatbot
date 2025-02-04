"""
Pydantic schemas for User authentication and registration for Lean Six Sigma RAG Chatbot.
This includes:
- UserBase: Base user information.
- UserCreate: Schema for user registration containing password.
- UserOut: Schema for user details output excluding password.
- Token: Schema for JWT authentication token.
- TokenData: Schema for token payload structure.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None 