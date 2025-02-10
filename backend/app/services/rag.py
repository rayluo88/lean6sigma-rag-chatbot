"""
RAG (Retrieval Augmented Generation) service for the Lean Six Sigma Chatbot.

This module handles:
- Document chunking and embedding
- Vector storage in Weaviate
- Context retrieval
- OpenAI integration for response generation
"""

import os
from typing import List, Dict, Any, Optional
import weaviate
from openai import OpenAI
import tiktoken
from pathlib import Path
import logging
from weaviate.exceptions import UnexpectedStatusCodeException, WeaviateBaseError

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Constants
CHUNK_OVERLAP = 200
MAX_TOKENS = 4000
EMBEDDING_MODEL = "text-embedding-3-small"
COMPLETION_MODEL = "gpt-3.5-turbo"

class RAGService:
    def __init__(self):
        """Initialize RAG service with Weaviate and OpenAI clients."""
        # Service configuration
        self.CHUNK_SIZE = 1000
        
        try:
            # Initialize clients
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.weaviate_client = weaviate.Client(
                url=settings.WEAVIATE_URL,
                additional_headers={
                    "X-OpenAI-Api-Key": settings.OPENAI_API_KEY
                }
            )
            logger.info("Initialized RAG service with Weaviate and OpenAI clients")
            
            # Ensure collection exists
            self._create_collection()
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
        
    def _create_collection(self):
        """Create or get Weaviate collection for LSS documents."""
        class_obj = {
            "class": "LSSDocument",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": EMBEDDING_MODEL,
                    "modelVersion": "3",
                    "type": "text"
                }
            },
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
        
        try:
            # Check if class exists
            self.weaviate_client.schema.get("LSSDocument")
            logger.info("LSSDocument collection already exists")
        except UnexpectedStatusCodeException:
            try:
                # Create new class if it doesn't exist
                self.weaviate_client.schema.create_class(class_obj)
                logger.info("Created LSSDocument collection")
            except WeaviateBaseError as e:
                logger.error(f"Failed to create collection: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error accessing schema: {e}")
            raise

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if not text.strip():
            logger.warning("Received empty text for chunking")
            return []
            
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.CHUNK_SIZE
            # If this is not the first chunk, include overlap
            if start > 0:
                start = start - CHUNK_OVERLAP
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            start = end
        
        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        try:
            encoding = tiktoken.encoding_for_model(COMPLETION_MODEL)
            return len(encoding.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Return a conservative estimate
            return len(text.split()) * 2

    def _get_metadata_value(self, metadata: Dict[str, Any], key: str, default: str = "") -> str:
        """Safely get metadata value with default."""
        try:
            value = metadata.get(key, default)
            return str(value) if value is not None else default
        except Exception as e:
            logger.warning(f"Error getting metadata value for {key}: {e}")
            return default

    async def index_document(self, content: str, metadata: Dict[str, Any]):
        """Index a document in Weaviate."""
        try:
            # Handle empty content
            if not content.strip():
                logger.warning("Received empty content for indexing")
                return
            
            chunks = self._chunk_text(content)
            logger.info(f"Indexing document with {len(chunks)} chunks")
            
            if not chunks:
                logger.warning("No valid chunks generated from content")
                return
            
            # Get metadata values safely
            category = self._get_metadata_value(metadata, "category")
            source = self._get_metadata_value(metadata, "source")
            
            # Create objects in batch
            with self.weaviate_client.batch as batch:
                for i, chunk in enumerate(chunks):
                    try:
                        batch.add_data_object(
                            data_object={
                                "content": chunk,
                                "category": category,
                                "source": source
                            },
                            class_name="LSSDocument"
                        )
                        logger.debug(f"Indexed chunk {i+1}/{len(chunks)}")
                    except Exception as e:
                        logger.error(f"Error indexing chunk {i}: {e}")
                        raise
            
            logger.info(f"Successfully indexed document from {source or 'unknown'}")
            
        except Exception as e:
            logger.error(f"Failed to index document: {e}")
            raise

    def _extract_object_data(self, obj: Dict[str, Any]) -> Dict[str, str]:
        """Safely extract data from Weaviate object."""
        return {
            "content": str(obj.get("content", "")),
            "category": str(obj.get("category", "")),
            "source": str(obj.get("source", ""))
        }

    async def retrieve_context(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant context from Weaviate based on query."""
        try:
            if not query.strip():
                logger.warning("Received empty query")
                return []
                
            response = (
                self.weaviate_client.query
                .get("LSSDocument", ["content", "category", "source"])
                .with_near_text({
                    "concepts": [query]
                })
                .with_limit(limit)
                .with_additional(["distance"])
                .do()
            )
            
            if response and "data" in response and "Get" in response["data"]:
                objects = response["data"]["Get"]["LSSDocument"]
                contexts = [
                    self._extract_object_data(obj)
                    for obj in objects
                ]
                logger.info(f"Retrieved {len(contexts)} contexts for query: {query}")
                return contexts
            
            logger.warning(f"No contexts found for query: {query}")
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def _build_prompt(self, query: str, contexts: List[Dict[str, Any]]) -> str:
        """Build prompt for OpenAI with query and retrieved contexts."""
        try:
            context_str = "\n\n".join([
                f"Context from {ctx['source'] or 'unknown'} ({ctx['category'] or 'uncategorized'}):\n{ctx['content']}"
                for ctx in contexts
            ])
            
            prompt = f"""You are an expert Lean Six Sigma consultant. Use the following context to answer the user's question.
            Be specific and cite relevant methodologies, tools, or concepts from the context when applicable.
            If you're not sure about something, be honest about it.

            Context:
            {context_str}

            User Question: {query}

            Answer:"""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error building prompt: {e}")
            # Return a simplified prompt without context
            return f"User Question: {query}\n\nAnswer:"

    async def generate_response(self, query: str) -> str:
        """Generate a response using RAG pipeline."""
        try:
            if not query.strip():
                logger.warning("Received empty query")
                return "I apologize, but I cannot generate a response for an empty question. Please provide a specific question about Lean Six Sigma."
            
            # Retrieve relevant contexts
            contexts = await self.retrieve_context(query)
            
            if not contexts:
                logger.warning("No context found for query, returning fallback response")
                return "I apologize, but I don't have enough context to provide a specific answer about that aspect of Lean Six Sigma. Could you please rephrase your question or ask about a different topic?"
            
            # Build prompt with contexts
            prompt = self._build_prompt(query, contexts)
            
            # Check token count
            token_count = self._count_tokens(prompt)
            if token_count > MAX_TOKENS:
                logger.warning(f"Prompt exceeds token limit ({token_count} > {MAX_TOKENS}), truncating contexts")
                # Truncate contexts if needed
                while token_count > MAX_TOKENS and contexts:
                    contexts.pop()
                    prompt = self._build_prompt(query, contexts)
                    token_count = self._count_tokens(prompt)
                
                if not contexts:
                    logger.warning("All contexts removed due to token limit")
                    return "I apologize, but the context required to answer your question is too large. Could you please ask a more specific question?"
            
            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model=COMPLETION_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Lean Six Sigma consultant providing accurate and helpful advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try again later."

# Create singleton instance
rag_service = RAGService() 