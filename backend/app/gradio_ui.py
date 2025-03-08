"""
Gradio UI for the Lean Six Sigma RAG Chatbot.

This module provides a web interface for the chatbot using Gradio.
"""

import os
import sys
import asyncio
import gradio as gr
import logging
from typing import List, Dict, Any
import json
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.services.rag import rag_service
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
TITLE = "Lean Six Sigma RAG Chatbot"
DESCRIPTION = """
This chatbot uses Retrieval Augmented Generation (RAG) to provide expert guidance on Lean Six Sigma methodologies.
Ask questions about DMAIC, Lean tools, Six Sigma concepts, or any other LSS-related topics.
"""
THEME = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="indigo",
)

# Chat history for the session
chat_history = []

async def process_query(message: str, history: List[List[str]]) -> tuple:
    """
    Process a user query and return the response.
    
    Args:
        message: The user's message
        history: The chat history from Gradio
        
    Returns:
        Tuple of (message, history, sources)
    """
    try:
        # Format history for the RAG service
        formatted_history = []
        for h in history:
            if len(h) >= 2:
                formatted_history.append({"role": "user", "content": h[0]})
                formatted_history.append({"role": "assistant", "content": h[1]})
        
        # Generate response
        result = await rag_service.generate_response(message, formatted_history)
        response_text = result["response"]
        sources = result.get("sources", [])
        
        # Format sources for display
        sources_text = ""
        if sources:
            sources_text = "### Sources\n\n"
            for i, source in enumerate(sources, 1):
                metadata = source.get("metadata", {})
                title = metadata.get("title", "Untitled")
                category = metadata.get("category", "Uncategorized")
                sources_text += f"**{i}. {title}** ({category})\n\n"
        
        return response_text, history + [[message, response_text]], sources_text
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        error_message = "I'm sorry, I encountered an error while processing your request. Please try again later."
        return error_message, history + [[message, error_message]], ""

def create_ui() -> gr.Blocks:
    """Create and configure the Gradio UI."""
    with gr.Blocks(title=TITLE, theme=THEME) as demo:
        gr.Markdown(f"# {TITLE}")
        gr.Markdown(DESCRIPTION)
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    height=600,
                    show_label=False,
                    bubble_full_width=False,
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask a question about Lean Six Sigma...",
                        show_label=False,
                        container=False,
                        scale=9,
                    )
                    submit_btn = gr.Button("Send", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat")
            
            with gr.Column(scale=1):
                sources_md = gr.Markdown(
                    "### Sources\n\nSources will appear here when you ask a question.",
                    label="Reference Sources",
                    height=600,
                )
        
        # Set up event handlers
        msg.submit(
            fn=process_query,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot, sources_md],
            queue=True,
        )
        
        submit_btn.click(
            fn=process_query,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot, sources_md],
            queue=True,
        )
        
        clear_btn.click(
            lambda: (None, [], "### Sources\n\nSources will appear here when you ask a question."),
            outputs=[msg, chatbot, sources_md],
        )
        
        # Add examples
        gr.Examples(
            examples=[
                "What is DMAIC and how is it used in Six Sigma?",
                "Explain the difference between Lean and Six Sigma.",
                "What are the key tools used in the Measure phase?",
                "How do I calculate process sigma level?",
                "What is a value stream map and how do I create one?",
            ],
            inputs=msg,
        )
        
        # Add footer
        gr.Markdown(
            "### About\n\n"
            "This chatbot uses LangChain and RAG technology to provide accurate information "
            "about Lean Six Sigma methodologies, tools, and concepts."
        )
    
    return demo

def launch_ui(port: int = 7860, share: bool = False):
    """Launch the Gradio UI."""
    demo = create_ui()
    demo.launch(server_name="0.0.0.0", server_port=port, share=share)

if __name__ == "__main__":
    launch_ui() 