#!/usr/bin/env python3
"""
DeepWiki Unified Startup Script

This script provides multiple ways to start DeepWiki services:
1. Web API only
2. MCP server only  
3. Both services together

Usage:
    python start_deepwiki.py --mode web          # Web API only
    python start_deepwiki.py --mode mcp          # MCP server only
    python start_deepwiki.py --mode both         # Both services (default)
    python start_deepwiki.py --help              # Show help
"""

import argparse
import asyncio
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeepWikiLauncher:
    """Manages launching and coordination of DeepWiki services"""
    
    def __init__(self):
        self.web_process = None
        self.mcp_process = None
        self.running = True
        
    def start_web_api(self, port=8001):
        """Start the web API server"""
        try:
            logger.info(f"Starting DeepWiki Web API on port {port}...")
            
            # Set environment variable to disable MCP in web mode
            env = os.environ.copy()
            env["ENABLE_MCP_SERVER"] = "false"
            env["PORT"] = str(port)
            
            # Set PYTHONPATH to include current directory
            env["PYTHONPATH"] = os.getcwd()

            self.web_process = subprocess.Popen(
                [sys.executable, "-m", "api.main"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor web API output in a separate thread
            def monitor_web():
                for line in iter(self.web_process.stdout.readline, ''):
                    if line.strip():
                        logger.info(f"[WEB] {line.strip()}")
                        
            web_monitor = threading.Thread(target=monitor_web, daemon=True)
            web_monitor.start()
            
            logger.info("Web API started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Web API: {str(e)}")
            return False
    
    def start_mcp_server(self):
        """Start the MCP server"""
        try:
            logger.info("Starting DeepWiki MCP Server...")

            # Set environment for MCP server
            env = os.environ.copy()
            env["PYTHONPATH"] = os.getcwd()

            self.mcp_process = subprocess.Popen(
                [sys.executable, "mcp_deepwiki.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor MCP server output in a separate thread
            def monitor_mcp():
                for line in iter(self.mcp_process.stdout.readline, ''):
                    if line.strip():
                        logger.info(f"[MCP] {line.strip()}")
                        
            mcp_monitor = threading.Thread(target=monitor_mcp, daemon=True)
            mcp_monitor.start()
            
            logger.info("MCP Server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP Server: {str(e)}")
            return False
    
    def stop_services(self):
        """Stop all running services"""
        logger.info("Stopping DeepWiki services...")
        self.running = False
        
        if self.web_process:
            try:
                self.web_process.terminate()
                self.web_process.wait(timeout=5)
                logger.info("Web API stopped")
            except subprocess.TimeoutExpired:
                self.web_process.kill()
                logger.warning("Web API force killed")
            except Exception as e:
                logger.error(f"Error stopping Web API: {str(e)}")
        
        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
                logger.info("MCP Server stopped")
            except subprocess.TimeoutExpired:
                self.mcp_process.kill()
                logger.warning("MCP Server force killed")
            except Exception as e:
                logger.error(f"Error stopping MCP Server: {str(e)}")
    
    def run_web_only(self, port=8001):
        """Run only the web API"""
        logger.info("Starting DeepWiki in Web API mode")
        
        if not self.start_web_api(port):
            return False
        
        try:
            # Wait for the web process
            while self.running and self.web_process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop_services()
        
        return True
    
    def run_mcp_only(self):
        """Run only the MCP server"""
        logger.info("Starting DeepWiki in MCP Server mode")
        
        if not self.start_mcp_server():
            return False
        
        try:
            # Wait for the MCP process
            while self.running and self.mcp_process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop_services()
        
        return True
    
    def run_both(self, port=8001):
        """Run both web API and MCP server"""
        logger.info("Starting DeepWiki in Combined mode (Web API + MCP Server)")
        
        # Start web API with MCP integration enabled
        env = os.environ.copy()
        env["ENABLE_MCP_SERVER"] = "true"
        env["PORT"] = str(port)
        env["PYTHONPATH"] = os.getcwd()
        
        try:
            logger.info(f"Starting integrated DeepWiki server on port {port}...")
            
            self.web_process = subprocess.Popen(
                [sys.executable, "-m", "api.main"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor output
            def monitor_combined():
                for line in iter(self.web_process.stdout.readline, ''):
                    if line.strip():
                        logger.info(f"[COMBINED] {line.strip()}")
                        
            monitor = threading.Thread(target=monitor_combined, daemon=True)
            monitor.start()
            
            logger.info("Combined server started successfully")
            logger.info(f"Web API available at: http://localhost:{port}")
            logger.info("MCP server components initialized and ready")
            logger.info("To use MCP with Claude Desktop:")
            logger.info("  mcp install mcp_deepwiki.py --name 'DeepWiki Code Assistant'")
            
            # Wait for the process
            while self.running and self.web_process.poll() is None:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop_services()
        
        return True

def setup_signal_handlers(launcher):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        launcher.stop_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="DeepWiki Unified Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_deepwiki.py                    # Start both services (default)
  python start_deepwiki.py --mode web         # Web API only
  python start_deepwiki.py --mode mcp         # MCP server only
  python start_deepwiki.py --mode both        # Both services
  python start_deepwiki.py --port 8080        # Custom port for web API
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["web", "mcp", "both"],
        default="both",
        help="Service mode to run (default: both)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port for web API (default: 8001)"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("api/main.py").exists():
        logger.error("Please run this script from the DeepWiki root directory")
        sys.exit(1)
    
    # Create launcher
    launcher = DeepWikiLauncher()
    
    # Setup signal handlers
    setup_signal_handlers(launcher)
    
    # Run based on mode
    success = False
    if args.mode == "web":
        success = launcher.run_web_only(args.port)
    elif args.mode == "mcp":
        success = launcher.run_mcp_only()
    elif args.mode == "both":
        success = launcher.run_both(args.port)
    
    if not success:
        logger.error("Failed to start DeepWiki services")
        sys.exit(1)

if __name__ == "__main__":
    main()
