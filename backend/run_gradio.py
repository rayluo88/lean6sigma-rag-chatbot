#!/usr/bin/env python3
"""
Run script for the Gradio UI of the Lean Six Sigma RAG Chatbot.

Usage:
    python run_gradio.py [--port PORT] [--share]
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.gradio_ui import launch_ui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Gradio UI for the Lean Six Sigma RAG Chatbot")
    parser.add_argument("--port", type=int, default=7860, help="Port to run the Gradio UI on")
    parser.add_argument("--share", action="store_true", help="Create a shareable link")
    return parser.parse_args()

def main():
    """Run the Gradio UI."""
    args = parse_args()
    logger.info(f"Starting Gradio UI on port {args.port} (share={args.share})")
    launch_ui(port=args.port, share=args.share)

if __name__ == "__main__":
    main() 