"""
Documentation API endpoints for the Lean Six Sigma RAG Chatbot.

This module provides endpoints for:
- Retrieving documentation content
- Listing available documents
- Searching documentation
"""

import os
from pathlib import Path
from typing import List, Dict
import yaml
from fastapi import APIRouter, HTTPException, status
import markdown

router = APIRouter()

# Path to knowledge base directory
KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge_base"


class DocumentMetadata:
    """Parse and validate document metadata from markdown files."""
    
    @staticmethod
    def parse_metadata(content: str) -> Dict:
        """Extract YAML metadata from markdown content."""
        if not content.startswith('---'):
            return {}
        
        try:
            # Find the second '---' that ends the YAML front matter
            end_idx = content.index('---', 3)
            yaml_content = content[3:end_idx]
            return yaml.safe_load(yaml_content)
        except Exception:
            return {}


@router.get("/list", response_model=List[Dict])
async def list_documents():
    """List all available documents in the knowledge base."""
    documents = []
    
    for root, _, files in os.walk(KNOWLEDGE_BASE_DIR):
        for file in files:
            if file.endswith('.md') and file != 'README.md':
                rel_path = os.path.relpath(os.path.join(root, file), KNOWLEDGE_BASE_DIR)
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    metadata = DocumentMetadata.parse_metadata(content)
                    
                    documents.append({
                        "path": rel_path,
                        "title": metadata.get('title', file),
                        "category": metadata.get('category', ''),
                        "subcategory": metadata.get('subcategory', ''),
                        "tags": metadata.get('tags', []),
                        "last_updated": metadata.get('last_updated', '')
                    })
    
    return documents


@router.get("/content/{path:path}")
async def get_document_content(path: str):
    """Retrieve the content of a specific document."""
    try:
        file_path = KNOWLEDGE_BASE_DIR / path
        
        if not file_path.is_file() or not str(file_path).endswith('.md'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Parse metadata and content
        metadata = DocumentMetadata.parse_metadata(content)
        
        # Convert markdown to HTML
        html_content = markdown.markdown(content)
        
        return {
            "metadata": metadata,
            "content": content,
            "html_content": html_content
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 