"""
Main application module for the Lean Six Sigma RAG Chatbot.

This module initializes the FastAPI application and includes all routes.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import gradio as gr
import logging

from app.api import chat, auth, docs, subscription
from app.gradio_ui import create_ui

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Lean Six Sigma RAG Chatbot API",
    description="API for the Lean Six Sigma RAG Chatbot",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(docs.router, prefix="/api/v1/docs", tags=["Documentation"])
app.include_router(subscription.router, prefix="/api/v1/subscription", tags=["Subscription"])

# Create Gradio UI for development/testing
gradio_app = create_ui().queue()
gradio_app = gr.mount_gradio_app(app, gradio_app, path="/chatbot")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint that provides links to API docs and chatbot UI."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Lean Six Sigma RAG Chatbot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                h1 {
                    color: #2c3e50;
                }
                .links {
                    display: flex;
                    gap: 20px;
                    margin-top: 30px;
                }
                .link-card {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 20px;
                    width: 45%;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }
                .link-card:hover {
                    transform: translateY(-5px);
                }
                a {
                    text-decoration: none;
                    color: #3498db;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h1>Lean Six Sigma RAG Chatbot</h1>
            <p>
                Welcome to the Lean Six Sigma RAG Chatbot service. This application provides
                expert guidance on Lean Six Sigma methodologies using Retrieval Augmented Generation.
            </p>
            <div class="links">
                <div class="link-card">
                    <h2>API Documentation</h2>
                    <p>Explore the API endpoints and documentation.</p>
                    <a href="/docs">View API Docs</a>
                </div>
                <div class="link-card">
                    <h2>Chatbot UI</h2>
                    <p>Use the Gradio-based chatbot interface.</p>
                    <a href="/chatbot">Open Chatbot</a>
                </div>
            </div>
        </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 