"""
Main application module for the Lean Six Sigma RAG Chatbot.

This is the entry point of the FastAPI application that:
- Configures the FastAPI application
- Sets up CORS middleware
- Includes API routes
- Provides health check endpoints
- Initializes all required services

The application serves as a RESTful API backend for the LSS chatbot system,
handling user authentication, chat interactions, and RAG-based responses.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Lean Six Sigma RAG Chatbot API",
    description="API for the Lean Six Sigma RAG-based chatbot system",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Lean Six Sigma RAG Chatbot API"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
    } 