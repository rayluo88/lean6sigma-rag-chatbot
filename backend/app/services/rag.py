"""
RAG (Retrieval Augmented Generation) service for the Lean Six Sigma Chatbot.

This module handles:
- Document chunking and embedding
- Vector storage in Weaviate
- Context retrieval
- LangChain integration for response generation
"""

import os
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
from dotenv import load_dotenv
import time

# LangChain imports
from langchain_community.vectorstores import Weaviate
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import Document

# Weaviate and OpenAI imports
import weaviate
from openai import OpenAI
import tiktoken
from weaviate.exceptions import UnexpectedStatusCodeException, WeaviateBaseError

from app.core.config import settings

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Constants
CHUNK_OVERLAP = 200
MAX_TOKENS = 4000
EMBEDDING_MODEL = "text-embedding-ada-002"  # Use stable model
COMPLETION_MODEL = "gpt-3.5-turbo-0125"    # Use specific model version
OPENAI_API_BASE = "https://api.openai.com/v1"  # OpenAI's default API endpoint
MAX_RETRIES = 3  # Maximum number of retries for operations
RETRY_DELAY = 1  # Delay between retries in seconds

class RAGService:
    def __init__(self):
        """Initialize RAG service with Weaviate and LangChain components."""
        # Service configuration
        self.CHUNK_SIZE = 1000
        self.weaviate_available = False
        self.vector_store = None
        self.qa_chain = None
        
        try:
            # Initialize OpenAI client
            self.openai_client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=OPENAI_API_BASE,
                timeout=60.0
            )
            
            # Initialize LangChain components
            self.embeddings = OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                base_url=OPENAI_API_BASE,
                timeout=60.0
            )
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
            
            # Initialize LLM with proper configuration
            self.llm = ChatOpenAI(
                model_name=COMPLETION_MODEL,
                temperature=0.2,
                openai_api_key=settings.OPENAI_API_KEY,
                base_url=OPENAI_API_BASE,
                timeout=60.0,
                streaming=False
            )
            logger.info(f"Using OpenAI chat model at {OPENAI_API_BASE}")
            
            # Create conversation memory (needed regardless of Weaviate availability)
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Initialize Weaviate client with retries
            self._initialize_weaviate()
            
            logger.info("Initialized RAG service with LangChain components")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise

    def _initialize_weaviate(self):
        """Initialize Weaviate client with retries."""
        for attempt in range(MAX_RETRIES):
            try:
                # Try without auth first (for local development)
                self.weaviate_client = weaviate.Client(
                    url=settings.WEAVIATE_URL,
                    timeout_config=(5, 60)  # (connect_timeout, read_timeout)
                )
                
                # Test connection
                self.weaviate_client.schema.get()
                logger.info("Connected to Weaviate without authentication")
                self.weaviate_available = True
                break
                
            except Exception as e:
                logger.warning(f"Failed to connect to Weaviate without auth (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                
                # Try with API key if available
                if settings.WEAVIATE_API_KEY:
                    try:
                        auth_config = weaviate.auth.AuthApiKey(api_key=settings.WEAVIATE_API_KEY)
                        self.weaviate_client = weaviate.Client(
                            url=settings.WEAVIATE_URL,
                            auth_client_secret=auth_config,
                            additional_headers={
                                "X-OpenAI-Api-Key": settings.OPENAI_API_KEY
                            },
                            timeout_config=(5, 60)
                        )
                        
                        # Test connection
                        self.weaviate_client.schema.get()
                        logger.info("Connected to Weaviate with API key authentication")
                        self.weaviate_available = True
                        break
                        
                    except Exception as e:
                        logger.error(f"Failed to connect to Weaviate with API key (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.warning("Failed to connect to Weaviate after all retries. Using fallback mode without RAG.")
                    self.weaviate_available = False
        
        # Only proceed with Weaviate setup if connection is successful
        if self.weaviate_available:
            try:
                # Ensure collection exists
                self._create_collection()
                
                # Initialize vector store
                self.vector_store = Weaviate(
                    client=self.weaviate_client,
                    index_name="LSSDocument",
                    text_key="content",
                    embedding=self.embeddings,
                    by_text=False,
                    retrieval_params={"distance_metric": "cosine"}
                )
                
                # Create retrieval chain
                self.qa_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=self.vector_store.as_retriever(
                        search_kwargs={"k": 3}
                    ),
                    memory=self.memory,
                    return_source_documents=True,
                    verbose=True
                )
            except Exception as e:
                logger.error(f"Failed to initialize vector store: {e}")
                self.weaviate_available = False
                self.vector_store = None
                self.qa_chain = None
        else:
            logger.warning("Weaviate is not available. Using fallback mode without RAG.")

    def _create_collection(self):
        """Create or get Weaviate collection for LSS documents."""
        if not self.weaviate_available:
            logger.warning("Weaviate is not available. Cannot create collection.")
            return
            
        class_obj = {
            "class": "LSSDocument",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The content of the document chunk"
                },
                {
                    "name": "title",
                    "dataType": ["string"],
                    "description": "The title of the document"
                },
                {
                    "name": "source",
                    "dataType": ["string"],
                    "description": "The source of the document"
                },
                {
                    "name": "category",
                    "dataType": ["string"],
                    "description": "The category of the document"
                }
            ],
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": EMBEDDING_MODEL,
                    "modelVersion": "latest",
                    "type": "text"
                }
            }
        }
        
        try:
            # Check if class exists
            if not self.weaviate_client.schema.exists("LSSDocument"):
                self.weaviate_client.schema.create_class(class_obj)
                logger.info("Created LSSDocument class in Weaviate")
            else:
                logger.info("LSSDocument class already exists in Weaviate")
        except Exception as e:
            logger.error(f"Failed to create Weaviate class: {e}")
            self.weaviate_available = False  # Mark Weaviate as unavailable if we can't create the class
            self.vector_store = None
            self.qa_chain = None

    def _count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        try:
            encoding = tiktoken.encoding_for_model(COMPLETION_MODEL)
            return len(encoding.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback to approximate count
            return len(text) // 4

    def _get_metadata_value(self, metadata: Dict[str, Any], key: str, default: str = "") -> str:
        """Safely extract metadata value with a default fallback."""
        return str(metadata.get(key, default))

    async def index_document(self, content: str, metadata: Dict[str, Any]):
        """
        Index a document into the vector store.
        
        Args:
            content: The document content
            metadata: Document metadata including title, source, category
        """
        try:
            # Check if Weaviate is available
            if not self.weaviate_available or not self.vector_store:
                logger.warning("Weaviate is not available. Cannot index document.")
                return False
                
            # Split text into chunks
            docs = self.text_splitter.create_documents(
                texts=[content],
                metadatas=[metadata]
            )
            
            # Convert to LangChain documents
            langchain_docs = [
                Document(
                    page_content=doc.page_content,
                    metadata={
                        "title": self._get_metadata_value(doc.metadata, "title"),
                        "source": self._get_metadata_value(doc.metadata, "source"),
                        "category": self._get_metadata_value(doc.metadata, "category")
                    }
                )
                for doc in docs
            ]
            
            # Add documents to vector store with retries
            for attempt in range(MAX_RETRIES):
                try:
                    self.vector_store.add_documents(langchain_docs)
                    logger.info(f"Indexed document: {metadata.get('title', 'Untitled')} with {len(docs)} chunks")
                    return True
                except Exception as e:
                    logger.error(f"Error indexing document (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                    else:
                        return False
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
            return False

    async def retrieve_context(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: The user query
            limit: Maximum number of context chunks to retrieve
            
        Returns:
            List of context chunks with metadata
        """
        try:
            # Check if Weaviate is available
            if not self.weaviate_available or not self.vector_store:
                logger.warning("Weaviate is not available. Cannot retrieve context.")
                return []
                
            # Use LangChain retriever to get relevant documents with retries
            for attempt in range(MAX_RETRIES):
                try:
                    docs = self.vector_store.similarity_search(
                        query=query,
                        k=limit
                    )
                    
                    # Format results
                    results = []
                    for doc in docs:
                        results.append({
                            "content": doc.page_content,
                            "metadata": doc.metadata
                        })
                    
                    logger.info(f"Retrieved {len(results)} context chunks for query: {query}")
                    return results
                except Exception as e:
                    logger.error(f"Error retrieving context (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                    else:
                        return []
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    async def generate_response(self, query: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate a response to a user query using LangChain.
        
        Args:
            query: The user query
            chat_history: Optional chat history for context
            
        Returns:
            Dictionary containing response text and source documents
        """
        try:
            # Reset memory for new conversation if no history provided
            if not chat_history:
                self.memory.clear()
            else:
                # Format history for LangChain memory
                for message in chat_history[-5:]:  # Use last 5 messages
                    if message.get("role") == "user":
                        self.memory.chat_memory.add_user_message(message.get("content", ""))
                    else:
                        self.memory.chat_memory.add_ai_message(message.get("content", ""))
            
            # Generate response using LangChain
            if self.weaviate_available and self.qa_chain:
                # Use RAG with Weaviate
                for attempt in range(MAX_RETRIES):
                    try:
                        result = self.qa_chain({"question": query})
                        
                        # Extract response and sources
                        response_text = result.get("answer", "")
                        source_documents = result.get("source_documents", [])
                        
                        # Format sources for return
                        sources = []
                        for doc in source_documents:
                            sources.append({
                                "content": doc.page_content,
                                "metadata": doc.metadata
                            })
                        break
                    except Exception as e:
                        logger.error(f"Error using RAG chain (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                        if attempt < MAX_RETRIES - 1:
                            time.sleep(RETRY_DELAY)
                            # Try to reinitialize Weaviate connection
                            self._initialize_weaviate()
                        else:
                            # Fall back to direct LLM if all retries fail
                            logger.warning("Falling back to direct LLM after RAG failures")
                            return await self._generate_fallback_response(query)
            else:
                # Use direct LLM without RAG
                return await self._generate_fallback_response(query)
            
            logger.info(f"Generated response for query: {query}")
            return {
                "response": response_text,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I'm sorry, I encountered an error while processing your request. Please try again later.",
                "sources": []
            }

    async def _generate_fallback_response(self, query: str) -> Dict[str, Any]:
        """Generate a response using direct LLM when RAG is unavailable."""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert Lean Six Sigma consultant providing accurate and helpful advice.
                Answer the user's question based on your knowledge of Lean Six Sigma methodologies, tools, and concepts.
                If you don't know the answer, be honest about it."""),
                ("human", "{question}")
            ])
            chain = prompt | self.llm
            response = chain.invoke({"question": query})
            return {
                "response": response.content,
                "sources": []  # No sources in fallback mode
            }
        except Exception as e:
            logger.error(f"Error generating fallback response: {e}")
            return {
                "response": "I'm sorry, I encountered an error while processing your request. Please try again later.",
                "sources": []
            }

# Initialize singleton service
rag_service = RAGService() 