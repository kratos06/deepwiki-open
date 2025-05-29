#!/usr/bin/env python3
"""
DeepWiki MCP Server Entry Point

This script provides a standalone entry point for the DeepWiki MCP server.
It can be used with MCP clients like Claude Desktop or other MCP-compatible applications.

Usage:
    # Direct execution
    python mcp_deepwiki.py

    # With MCP CLI for development
    mcp dev mcp_deepwiki.py

    # Install in Claude Desktop
    mcp install mcp_deepwiki.py --name "DeepWiki Code Assistant"

Environment Variables:
    GOOGLE_API_KEY: Google Gemini API key (required for Google provider)
    OPENAI_API_KEY: OpenAI API key (required for OpenAI provider and embeddings)
    OPENROUTER_API_KEY: OpenRouter API key (optional, for OpenRouter provider)
    OLLAMA_HOST: Ollama host URL (optional, default: http://localhost:11434)
"""

import sys
import os

# Add the current directory to the path so we can import the api module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the MCP server
from api.mcp_server import mcp

if __name__ == "__main__":
    print("Starting DeepWiki MCP Server...")
    print("Available tools:")
    print("  - ask_deepwiki: Ask questions about code repositories")
    print("  - query_code: Query code using RAG")
    print("  - get_file_content: Get content of specific files")
    print("")
    print("Available resources:")
    print("  - repo://structure/{repo_url}: Get repository structure")
    print("  - wiki://cache/{owner}/{repo}/{repo_type}/{language}: Get cached wiki data")
    print("  - repo://files/{repo_url}: Get list of repository files")
    print("")
    print("Available prompts:")
    print("  - analyze_code_structure: Analyze codebase structure")
    print("  - debug_code_issue: Debug code issues")
    print("  - explain_code_functionality: Explain code functionality")
    print("  - code_review_checklist: Code review checklist")
    print("")
    
    # Run the MCP server
    mcp.run()
