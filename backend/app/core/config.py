"""
Core configuration module for the Lean Six Sigma RAG Chatbot.

This module defines the application settings and environment variables using Pydantic.
It handles configuration for:
- Basic application settings
- Database connections
- Authentication
- External services (OpenAI, Weaviate)
- Security settings

The settings are loaded from environment variables or .env file.
"""

from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lean Six Sigma RAG Chatbot"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    ENVIRONMENT: str = "development"
    BACKEND_PORT: int = 8000
    
    # PostgreSQL
    DATABASE_URL: PostgresDsn
    
    # Weaviate
    WEAVIATE_URL: str
    WEAVIATE_API_KEY: Optional[str] = None
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI
    OPENAI_API_KEY: str
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # Allow extra fields in the settings

settings = Settings() 