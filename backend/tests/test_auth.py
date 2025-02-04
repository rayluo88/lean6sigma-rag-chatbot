"""
Integration tests for authentication endpoints in the Lean Six Sigma RAG Chatbot.

This module contains tests for:
- User registration endpoint (/register)
- User login endpoint (/login)

Usage:
    1. Ensure you are in the backend directory
    2. Make sure all dependencies are installed:
       pip install -r requirements.txt
    
    3. Run the tests using pytest:
       pytest tests/test_auth.py -v
       
    Optional pytest arguments:
    -v          : Verbose output
    -s          : Show print statements
    --pdb       : Debug on error
    --cov=app   : Show coverage report

Note: These tests require a running PostgreSQL database as configured 
      in the .env file or environment variables.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_register_and_login():
    # Test user registration
    register_payload = {
        "email": "testuser@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "testuser@example.com"

    # Test user login
    login_payload = {
        "email": "testuser@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data 