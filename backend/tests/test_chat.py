"""
Integration tests for chat endpoints in the Lean Six Sigma RAG Chatbot.

This module contains tests for:
- Chat endpoint (/api/v1/chat/chat)
- Authentication verification
- Response handling
- Chat history creation

Usage:
    1. Ensure you are in the backend directory
    2. Make sure all dependencies are installed:
       pip install -r requirements.txt
    
    3. Run the tests using pytest:
       pytest tests/test_chat.py -v -s
       
    Optional pytest arguments:
    -v          : Verbose output
    -s          : Show print statements (required to see query/response output)
    --pdb       : Debug on error
    --cov=app   : Show coverage report

Note: These tests require:
      - A running PostgreSQL database as configured in .env
      - Valid authentication credentials
      - The auth endpoints to be functioning correctly
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


def get_test_token():
    """Helper function to get a valid authentication token for testing."""
    # Register a test user
    register_payload = {
        "email": "chattest@example.com",
        "password": "testpassword",
        "full_name": "Chat Test User"
    }
    client.post("/api/v1/auth/register", json=register_payload)
    
    # Login to get token
    login_response = client.post("/api/v1/auth/login", json=register_payload)
    return login_response.json()["access_token"]


def test_chat_endpoint_authentication():
    """Test that chat endpoint requires authentication."""
    # Try without authentication
    chat_payload = {"query": "What is Six Sigma?"}
    print("\nTesting unauthenticated access:")
    print(f"Query: {chat_payload['query']}")
    
    response = client.post("/api/v1/chat/chat", json=chat_payload)
    print(f"Response Status: {response.status_code} (Expected: 401 Unauthorized)")
    assert response.status_code == 401  # Unauthorized
    
    # Try with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    print("\nTesting invalid token:")
    response = client.post("/api/v1/chat/chat", json=chat_payload, headers=headers)
    print(f"Response Status: {response.status_code} (Expected: 401 Unauthorized)")
    assert response.status_code == 401  # Unauthorized


def test_chat_endpoint_with_auth():
    """Test chat endpoint with valid authentication."""
    # Get valid token
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test chat query
    chat_payload = {"query": "What is Six Sigma?"}
    print("\nTesting authenticated chat:")
    print(f"Query: {chat_payload['query']}")
    
    response = client.post("/api/v1/chat/chat", json=chat_payload, headers=headers)
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    print(f"Response Status: {response.status_code}")
    print(f"Response Content: {data['response']}")
    
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


def test_chat_invalid_query():
    """Test chat endpoint with invalid query format."""
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with empty query
    print("\nTesting empty query:")
    response = client.post("/api/v1/chat/chat", json={"query": ""}, headers=headers)
    print(f"Response Status: {response.status_code} (Expected: 422 Unprocessable Entity)")
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with missing query field
    print("\nTesting missing query field:")
    response = client.post("/api/v1/chat/chat", json={}, headers=headers)
    print(f"Response Status: {response.status_code} (Expected: 422 Unprocessable Entity)")
    assert response.status_code == 422  # Unprocessable Entity 