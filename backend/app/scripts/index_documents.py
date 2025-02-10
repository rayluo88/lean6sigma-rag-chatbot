"""
Script to index Lean Six Sigma knowledge base documents into Weaviate.

This script:
1. Walks through the knowledge base directory
2. Reads markdown files
3. Extracts content and metadata
4. Indexes documents using the RAG service
"""

import asyncio
import os
from pathlib import Path
import yaml
import logging
from typing import Dict, Any

from app.services.rag import rag_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to knowledge base directory
KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge_base"

async def extract_metadata(content: str) -> Dict[str, Any]:
    """Extract YAML metadata from markdown content."""
    if not content.startswith('---'):
        return {}
    
    try:
        # Find the second '---' that ends the YAML front matter
        end_idx = content.index('---', 3)
        yaml_content = content[3:end_idx]
        return yaml.safe_load(yaml_content)
    except Exception as e:
        logger.error(f"Error parsing metadata: {e}")
        return {}

async def process_file(file_path: Path):
    """Process a single markdown file."""
    try:
        # Read file content
        content = file_path.read_text(encoding='utf-8')
        
        # Extract metadata
        metadata = await extract_metadata(content)
        
        # Remove metadata section from content if it exists
        if content.startswith('---'):
            try:
                end_idx = content.index('---', 3)
                content = content[end_idx + 3:].strip()
            except ValueError:
                pass
        
        # Add source information to metadata
        rel_path = file_path.relative_to(KNOWLEDGE_BASE_DIR)
        metadata['source'] = str(rel_path)
        
        # Index the document
        await rag_service.index_document(content, metadata)
        logger.info(f"Indexed document: {rel_path}")
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")

async def main():
    """Main function to walk through knowledge base and index documents."""
    logger.info("Starting document indexing...")
    
    # Walk through knowledge base directory
    for root, _, files in os.walk(KNOWLEDGE_BASE_DIR):
        for file in files:
            if file.endswith('.md') and file != 'README.md':
                file_path = Path(root) / file
                await process_file(file_path)
    
    logger.info("Document indexing completed.")

if __name__ == "__main__":
    asyncio.run(main()) 