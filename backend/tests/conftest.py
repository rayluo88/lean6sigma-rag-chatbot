"""
Test configuration and fixtures for the Lean Six Sigma RAG Chatbot.

This module provides:
- Common test fixtures
- Environment setup
- Mock clients and utilities
- Error simulation
"""

import os
import pytest
from unittest.mock import MagicMock, PropertyMock
import weaviate
from weaviate.exceptions import UnexpectedStatusCodeException, WeaviateBaseError
import logging
from pathlib import Path
import requests

# Add backend to Python path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in os.sys.path:
    os.sys.path.append(str(backend_dir))

from app.core.config import settings

# Mock response for UnexpectedStatusCodeException
mock_response = requests.Response()
mock_response.status_code = 404
mock_response._content = b'{"error": "Not Found"}'

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["WEAVIATE_URL"] = "http://localhost:8080"
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["JWT_SECRET"] = "test-secret"
    yield
    # Cleanup
    os.environ.pop("ENVIRONMENT", None)

@pytest.fixture
def mock_weaviate_client():
    """Create a mock Weaviate client with detailed response handling."""
    client = MagicMock(spec=weaviate.Client)
    
    # Mock schema operations
    schema = MagicMock()
    schema.get.return_value = {
        "class": "LSSDocument",
        "vectorizer": "text2vec-openai",
        "properties": [
            {
                "name": "content",
                "dataType": ["text"],
                "description": "Document content",
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": False,
                        "vectorizePropertyName": False
                    }
                }
            },
            {
                "name": "category",
                "dataType": ["text"],
                "description": "Document category",
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": True,
                        "vectorizePropertyName": False
                    }
                }
            },
            {
                "name": "source",
                "dataType": ["text"],
                "description": "Document source path",
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": True,
                        "vectorizePropertyName": False
                    }
                }
            }
        ]
    }
    schema.create_class.return_value = None
    client.schema = schema
    
    # Mock batch operations
    batch = MagicMock()
    batch.__enter__ = MagicMock(return_value=batch)
    batch.__exit__ = MagicMock(return_value=None)
    batch.add_data_object = MagicMock()
    client.batch = batch
    
    # Mock query builder with chainable methods
    query = MagicMock()
    query.get.return_value = query
    query.with_near_text.return_value = query
    query.with_limit.return_value = query
    query.with_additional.return_value = query
    
    # Default successful query response
    query.do.return_value = {
        "data": {
            "Get": {
                "LSSDocument": [
                    {
                        "content": "Test content about DMAIC methodology",
                        "category": "Methodology",
                        "source": "methodology/dmaic.md",
                        "_additional": {
                            "distance": 0.8
                        }
                    },
                    {
                        "content": "Another test content about Six Sigma",
                        "category": "Overview",
                        "source": "overview/six_sigma.md",
                        "_additional": {
                            "distance": 0.9
                        }
                    }
                ]
            }
        }
    }
    client.query = query
    
    return client

@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client with detailed response handling."""
    client = MagicMock()
    
    # Mock chat completions
    chat = MagicMock()
    completion = MagicMock()
    message = MagicMock()
    
    # Default successful response
    message.content = "This is a test response about DMAIC methodology. DMAIC stands for Define, Measure, Analyze, Improve, and Control. It is a core process improvement methodology in Six Sigma."
    completion.choices = [MagicMock(message=message)]
    chat.completions.create.return_value = completion
    client.chat = chat
    
    return client

@pytest.fixture
def test_content():
    """Sample test content with metadata section."""
    return """---
title: DMAIC Methodology
category: Methodology
tags:
  - process improvement
  - six sigma
---

# DMAIC Methodology

DMAIC is a data-driven quality strategy used to improve processes.
It is an integral part of Six Sigma methodology.

## Overview

DMAIC stands for:
- Define
- Measure
- Analyze
- Improve
- Control

Each phase has specific goals and deliverables.
"""

@pytest.fixture
def test_metadata():
    """Sample test metadata."""
    return {
        "title": "DMAIC Methodology",
        "category": "Methodology",
        "source": "methodology/dmaic.md",
        "tags": ["process improvement", "six sigma"]
    }

@pytest.fixture
def error_mock_weaviate_client(mock_weaviate_client):
    """Create a Weaviate client that simulates various errors."""
    # Schema errors
    mock_weaviate_client.schema.get.side_effect = UnexpectedStatusCodeException(mock_response)
    mock_weaviate_client.schema.create_class.side_effect = WeaviateBaseError("Failed to create schema")
    
    # Batch errors
    batch = MagicMock()
    batch.__enter__ = MagicMock(return_value=batch)
    batch.__exit__ = MagicMock(return_value=None)
    batch.add_data_object.side_effect = Exception("Failed to add object")
    mock_weaviate_client.batch = batch
    
    # Query errors
    query = MagicMock()
    query.get.return_value = query
    query.with_near_text.return_value = query
    query.with_limit.return_value = query
    query.with_additional.return_value = query
    query.do.side_effect = Exception("Query failed")
    mock_weaviate_client.query = query
    
    return mock_weaviate_client

@pytest.fixture
def error_mock_openai_client(mock_openai_client):
    """Create an OpenAI client that simulates various errors."""
    chat = MagicMock()
    chat.completions.create.side_effect = Exception("OpenAI API error")
    mock_openai_client.chat = chat
    return mock_openai_client 