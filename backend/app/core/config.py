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
from pydantic import PostgresDsn, field_validator, ConfigDict, BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow"
    )
    
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
    
    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: Optional[str]) -> Any:
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v
    
    @field_validator("WEAVIATE_URL")
    def validate_weaviate_url(cls, v: Optional[str]) -> Any:
        if not v:
            raise ValueError("WEAVIATE_URL must be set")
        return v
    
    @field_validator("OPENAI_API_KEY")
    def validate_openai_api_key(cls, v: Optional[str]) -> Any:
        if not v:
            raise ValueError("OPENAI_API_KEY must be set")
        return v

settings = Settings() 