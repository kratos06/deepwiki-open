"""
MCP Service Manager for DeepWiki

This module manages the MCP server as part of the DeepWiki application lifecycle.
It handles starting and stopping the MCP server alongside the main FastAPI application.
"""

import logging
import os
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class MCPServiceManager:
    """Manages the MCP server lifecycle within the DeepWiki application"""
    
    def __init__(self):
        self.mcp_server = None
        self.mcp_thread = None
        self.is_running = False
        self.should_stop = False
        
    async def start_mcp_server(self):
        """Initialize MCP server components (but don't start stdio server)"""
        try:
            # Import MCP server components here to avoid circular imports
            try:
                from api.mcp_server import mcp
            except ImportError:
                # Fallback for when running as subprocess
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from api.mcp_server import mcp

            logger.info("Initializing MCP server components...")

            # Store reference to MCP server for later use
            self.mcp_server = mcp
            self.is_running = True

            logger.info("MCP server components initialized successfully")
            logger.info("MCP server is ready for stdio connections")
            logger.info("To use MCP server with Claude Desktop:")
            logger.info("  mcp install mcp_deepwiki.py --name 'DeepWiki Code Assistant'")
            logger.info("To test MCP server:")
            logger.info("  mcp dev mcp_deepwiki.py")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {str(e)}")
            return False
    
    async def stop_mcp_server(self):
        """Stop the MCP server"""
        try:
            if self.is_running:
                logger.info("Stopping MCP server components...")
                self.is_running = False
                self.mcp_server = None
                logger.info("MCP server components stopped")

        except Exception as e:
            logger.error(f"Error stopping MCP server: {str(e)}")
    
    def get_status(self) -> dict:
        """Get the current status of the MCP server"""
        return {
            "running": self.is_running,
            "initialized": self.mcp_server is not None,
            "ready_for_connections": self.is_running
        }

# Global MCP service manager instance
mcp_service = MCPServiceManager()

@asynccontextmanager
async def mcp_lifespan_manager(app):
    """
    Lifespan context manager for FastAPI that handles MCP server startup and shutdown
    """
    # Startup
    logger.info("Starting DeepWiki services...")
    
    # Check if MCP should be enabled
    enable_mcp = os.environ.get("ENABLE_MCP_SERVER", "true").lower() == "true"
    
    if enable_mcp:
        success = await mcp_service.start_mcp_server()
        if success:
            # Store the MCP service in app state for access in endpoints
            app.state.mcp_server = mcp_service
            logger.info("MCP server integrated successfully")
        else:
            logger.warning("MCP server failed to start, continuing without MCP support")
    else:
        logger.info("MCP server disabled via ENABLE_MCP_SERVER environment variable")
    
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down DeepWiki services...")
        if enable_mcp and hasattr(app.state, 'mcp_server'):
            await mcp_service.stop_mcp_server()
        logger.info("DeepWiki services shutdown complete")

def get_mcp_info() -> dict:
    """Get information about the MCP server for API responses"""
    if mcp_service.is_running:
        return {
            "status": "running",
            "description": "MCP server is running and available for Claude Desktop integration",
            "tools": [
                "ask_deepwiki - Intelligent code Q&A using RAG",
                "query_code - Quick code retrieval", 
                "get_file_content - Get specific file content"
            ],
            "resources": [
                "repo://structure/{repo_url} - Repository structure",
                "wiki://cache/{owner}/{repo}/{type}/{lang} - Cached wiki data",
                "repo://files/{repo_url}/{pattern} - File listings"
            ],
            "prompts": [
                "analyze_code_structure - Code architecture analysis",
                "debug_code_issue - Debugging assistance",
                "explain_code_functionality - Code explanation",
                "code_review_checklist - Review guidelines"
            ],
            "usage": {
                "claude_desktop": "Install with: mcp install mcp_deepwiki.py --name 'DeepWiki'",
                "development": "Test with: mcp dev mcp_deepwiki.py"
            }
        }
    else:
        return {
            "status": "not_running",
            "description": "MCP server is not currently running",
            "note": "Set ENABLE_MCP_SERVER=true to enable MCP integration"
        }

# Add MCP status endpoint function that can be imported
async def get_mcp_status():
    """Get detailed MCP server status"""
    status = mcp_service.get_status()
    info = get_mcp_info()
    
    return {
        "mcp_server": {
            **status,
            **info
        }
    }
