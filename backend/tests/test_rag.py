"""
Integration tests for RAG service with Weaviate v3.24.2.

This module tests:
- Weaviate collection creation
- Document indexing
- Context retrieval
- Error handling
- Logging functionality

Usage:
    1. Ensure you are in the backend directory
    2. Make sure all dependencies are installed:
       pip install -r requirements.txt
    
    3. Run the tests using pytest:
       pytest tests/test_rag.py -v
       
    Optional pytest arguments:
    -v          : Verbose output
    -s          : Show print statements
    --pdb       : Debug on error
    --cov=app   : Show coverage report

Note: These tests require:
      - A running Weaviate instance as configured in .env
      - OpenAI API key for embeddings
"""

import os
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock, call
import weaviate
from weaviate.exceptions import UnexpectedStatusCodeException, WeaviateBaseError
import logging

# Add the parent directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.services.rag import RAGService, EMBEDDING_MODEL

# Test data
TEST_CONTENT = """
# Test Document

This is a test document for the RAG service.
It contains some content about Lean Six Sigma.

## DMAIC Methodology
Define, Measure, Analyze, Improve, Control
"""

TEST_METADATA = {
    "category": "Test",
    "source": "test/document.md"
}

@pytest.fixture
def caplog(caplog):
    """Configure logging capture."""
    caplog.set_level(logging.INFO)
    return caplog

@pytest.fixture
def rag_service(mock_weaviate_client, mock_openai_client):
    """Create a RAG service instance for testing with mocked clients."""
    with patch('app.services.rag.weaviate.Client', return_value=mock_weaviate_client), \
         patch('app.services.rag.OpenAI', return_value=mock_openai_client):
        service = RAGService()
        # Inject mock clients
        service.weaviate_client = mock_weaviate_client
        service.openai_client = mock_openai_client
        return service

@pytest.fixture
def error_rag_service(error_mock_weaviate_client, error_mock_openai_client):
    """Create a RAG service instance for testing error scenarios."""
    with patch('app.services.rag.weaviate.Client', return_value=error_mock_weaviate_client), \
         patch('app.services.rag.OpenAI', return_value=error_mock_openai_client):
        service = RAGService()
        # Inject mock clients
        service.weaviate_client = error_mock_weaviate_client
        service.openai_client = error_mock_openai_client
        return service

def test_create_collection_existing(rag_service, mock_weaviate_client, caplog):
    """Test Weaviate collection creation when collection exists."""
    # Reset logging
    caplog.clear()
    
    # Create new service to trigger collection creation
    with patch('app.services.rag.weaviate.Client', return_value=mock_weaviate_client):
        RAGService()
    
    # Verify schema
    schema = mock_weaviate_client.schema.get("LSSDocument")
    assert schema is not None
    assert schema["class"] == "LSSDocument"
    assert schema["vectorizer"] == "text2vec-openai"
    
    # Verify properties
    properties = {prop["name"]: prop for prop in schema["properties"]}
    assert "content" in properties
    assert not properties["content"]["moduleConfig"]["text2vec-openai"]["skip"]
    assert "category" in properties
    assert properties["category"]["moduleConfig"]["text2vec-openai"]["skip"]
    assert "source" in properties
    assert properties["source"]["moduleConfig"]["text2vec-openai"]["skip"]
    
    # Verify logging
    assert "LSSDocument collection already exists" in caplog.text

def test_create_collection_new(rag_service, mock_weaviate_client, caplog):
    """Test Weaviate collection creation when collection doesn't exist."""
    # Reset logging
    caplog.clear()
    
    # Mock schema.get to raise exception
    mock_weaviate_client.schema.get.side_effect = UnexpectedStatusCodeException(mock_response)
    
    # Create new RAG service instance
    with patch('app.services.rag.weaviate.Client', return_value=mock_weaviate_client):
        RAGService()
    
    # Verify schema creation was called
    mock_weaviate_client.schema.create_class.assert_called_once()
    assert "Created LSSDocument collection" in caplog.text

def test_create_collection_error(error_mock_weaviate_client, caplog):
    """Test error handling in collection creation."""
    # Reset logging
    caplog.clear()
    
    with pytest.raises(WeaviateBaseError) as exc_info:
        RAGService()
    assert "Failed to create schema" in str(exc_info.value)
    assert "Failed to create collection" in caplog.text

@pytest.mark.asyncio
async def test_index_document_success(rag_service, test_content, test_metadata, caplog):
    """Test successful document indexing with logging."""
    # Reset logging
    caplog.clear()
    
    await rag_service.index_document(test_content, test_metadata)
    
    # Verify batch operations
    batch = rag_service.weaviate_client.batch
    batch.add_data_object.assert_called()
    
    # Verify logging
    assert f"Indexing document with" in caplog.text
    assert f"Successfully indexed document from {test_metadata['source']}" in caplog.text

@pytest.mark.asyncio
async def test_index_document_batch_error(error_rag_service, test_content, test_metadata, caplog):
    """Test error handling in batch operations."""
    # Reset logging
    caplog.clear()
    
    with pytest.raises(Exception) as exc_info:
        await error_rag_service.index_document(test_content, test_metadata)
    
    assert "Failed to add object" in str(exc_info.value)
    assert "Error indexing chunk" in caplog.text
    assert "Failed to index document" in caplog.text

@pytest.mark.asyncio
async def test_retrieve_context_success(rag_service, caplog):
    """Test successful context retrieval with logging."""
    # Reset logging
    caplog.clear()
    
    contexts = await rag_service.retrieve_context("test query")
    
    # Verify query construction
    query = rag_service.weaviate_client.query
    query.get.assert_called_with("LSSDocument", ["content", "category", "source"])
    query.with_near_text.assert_called_with({"concepts": ["test query"]})
    query.with_limit.assert_called()
    query.with_additional.assert_called_with(["distance"])
    
    # Verify response processing
    assert len(contexts) == 2
    assert contexts[0]["content"] == "Test content about DMAIC methodology"
    assert contexts[0]["category"] == "Methodology"
    assert contexts[0]["source"] == "methodology/dmaic.md"
    
    # Verify logging
    assert "Retrieved 2 contexts for query: test query" in caplog.text

@pytest.mark.asyncio
async def test_retrieve_context_query_error(error_rag_service, caplog):
    """Test error handling in context retrieval."""
    # Reset logging
    caplog.clear()
    
    contexts = await error_rag_service.retrieve_context("test query")
    
    assert len(contexts) == 0
    assert "Error retrieving context: Query failed" in caplog.text

@pytest.mark.asyncio
async def test_generate_response_success(rag_service, caplog):
    """Test successful response generation."""
    # Reset logging
    caplog.clear()
    
    response = await rag_service.generate_response("What is DMAIC?")
    
    assert isinstance(response, str)
    assert "DMAIC stands for Define, Measure, Analyze, Improve, and Control" in response
    assert "core process improvement methodology in Six Sigma" in response

@pytest.mark.asyncio
async def test_generate_response_no_context(rag_service, caplog):
    """Test response generation with no context."""
    # Reset logging
    caplog.clear()
    
    # Override mock response for empty results
    rag_service.weaviate_client.query.do.return_value = {
        "data": {
            "Get": {
                "LSSDocument": []
            }
        }
    }
    
    response = await rag_service.generate_response("What is DMAIC?")
    assert "I apologize" in response
    assert "rephrase your question" in response
    assert "No context found for query, returning fallback response" in caplog.text

@pytest.mark.asyncio
async def test_generate_response_token_limit(rag_service, caplog):
    """Test response generation with token limit handling."""
    # Reset logging
    caplog.clear()
    
    # Create a very long context that will exceed token limit
    long_context = {
        "data": {
            "Get": {
                "LSSDocument": [
                    {
                        "content": "x" * 10000,
                        "category": "Test",
                        "source": "test.md",
                        "_additional": {"distance": 0.8}
                    }
                ]
            }
        }
    }
    rag_service.weaviate_client.query.do.return_value = long_context
    
    # Mock token counting to ensure we exceed the limit
    with patch('tiktoken.encoding_for_model') as mock_encoding:
        mock_encode = MagicMock()
        mock_encode.encode.return_value = ["x"] * 5000  # Exceed MAX_TOKENS
        mock_encoding.return_value = mock_encode
        
        response = await rag_service.generate_response("What is DMAIC?")
    
    assert isinstance(response, str)
    assert "Prompt exceeds token limit" in caplog.text

@pytest.mark.asyncio
async def test_generate_response_openai_error(error_rag_service, caplog):
    """Test error handling in OpenAI response generation."""
    # Reset logging
    caplog.clear()
    
    response = await error_rag_service.generate_response("What is DMAIC?")
    assert "I apologize, but I encountered an error" in response
    assert "Error generating response: OpenAI API error" in caplog.text

def test_count_tokens_error(rag_service, caplog):
    """Test error handling in token counting."""
    # Reset logging
    caplog.clear()
    
    with patch('tiktoken.encoding_for_model', side_effect=Exception("Tiktoken error")):
        token_count = rag_service._count_tokens("Test text")
        
        # Should return conservative estimate
        assert token_count == 4  # 2 words * 2
        assert "Error counting tokens: Tiktoken error" in caplog.text

def test_chunk_text(rag_service):
    """Test text chunking functionality."""
    # Create a long text that should be split into multiple chunks
    long_text = "word " * 1000
    chunks = rag_service._chunk_text(long_text)
    
    # Verify chunks
    assert len(chunks) > 1
    for chunk in chunks:
        # Each chunk should be no longer than CHUNK_SIZE
        assert len(chunk.split()) <= rag_service.CHUNK_SIZE

@pytest.mark.asyncio
async def test_index_document_empty_content(rag_service, test_metadata, caplog):
    """Test indexing document with empty content."""
    # Reset logging
    caplog.clear()
    
    await rag_service.index_document("", test_metadata)
    
    # Verify no batch operations were performed
    batch = rag_service.weaviate_client.batch
    batch.add_data_object.assert_not_called()
    
    # Verify logging
    assert "Received empty content for indexing" in caplog.text

@pytest.mark.asyncio
async def test_index_document_missing_metadata(rag_service, test_content, caplog):
    """Test indexing document with missing metadata."""
    # Reset logging
    caplog.clear()
    
    await rag_service.index_document(test_content, {})
    
    # Verify batch operations used default values
    batch = rag_service.weaviate_client.batch
    call_args = batch.add_data_object.call_args_list[0]
    assert call_args.kwargs['data_object']['category'] == ""
    assert call_args.kwargs['data_object']['source'] == ""

@pytest.mark.asyncio
async def test_retrieve_context_malformed_response(rag_service, caplog):
    """Test handling of malformed response from Weaviate."""
    # Reset logging
    caplog.clear()
    
    # Override mock response with malformed data
    rag_service.weaviate_client.query.do.return_value = {
        "data": {
            "Get": {
                "LSSDocument": [
                    {
                        # Missing required fields
                        "some_field": "some_value"
                    }
                ]
            }
        }
    }
    
    contexts = await rag_service.retrieve_context("test query")
    assert len(contexts) == 1
    assert contexts[0]["content"] == ""  # Should use default values
    assert contexts[0]["category"] == ""
    assert contexts[0]["source"] == "" 