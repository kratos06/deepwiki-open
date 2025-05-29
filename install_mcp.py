#!/usr/bin/env python3
"""
Installation script for DeepWiki MCP Server

This script installs the required dependencies and sets up the MCP server.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Install from requirements.txt
    if not run_command("pip install -r api/requirements.txt", "Installing Python dependencies"):
        return False
    
    return True

def verify_installation():
    """Verify that MCP is installed correctly"""
    print("🔍 Verifying installation...")
    
    try:
        import mcp
        print("✅ MCP package is available")
        return True
    except ImportError:
        print("❌ MCP package not found")
        return False

def create_example_config():
    """Create an example configuration file"""
    config_content = """# DeepWiki MCP Server Configuration
# Copy this to .env and fill in your API keys

# Required for most functionality
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional providers
OPENROUTER_API_KEY=your_openrouter_api_key_here
OLLAMA_HOST=http://localhost:11434

# Optional configuration
DEEPWIKI_CONFIG_DIR=./api/config
"""
    
    if not os.path.exists(".env.example"):
        with open(".env.example", "w") as f:
            f.write(config_content)
        print("✅ Created .env.example file")
    else:
        print("ℹ️  .env.example already exists")

def show_usage_instructions():
    """Show usage instructions"""
    print("\n" + "="*60)
    print("🎉 Installation completed successfully!")
    print("="*60)
    
    print("\n📋 Next steps:")
    print("1. Copy .env.example to .env and add your API keys:")
    print("   cp .env.example .env")
    print("   # Edit .env with your favorite editor")
    
    print("\n2. Test the MCP server:")
    print("   python test_mcp_server.py")
    
    print("\n3. Run the MCP server:")
    print("   python mcp_deepwiki.py")
    
    print("\n4. Install in Claude Desktop:")
    print("   mcp install mcp_deepwiki.py --name 'DeepWiki Code Assistant'")
    
    print("\n5. Or use with MCP development tools:")
    print("   mcp dev mcp_deepwiki.py")
    
    print("\n📚 Documentation:")
    print("   - See MCP_README.md for detailed usage instructions")
    print("   - See README.md for general DeepWiki documentation")

def main():
    """Main installation function"""
    print("🚀 DeepWiki MCP Server Installation")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed.")
        print("You may need to restart your terminal or virtual environment.")
        sys.exit(1)
    
    # Create example config
    create_example_config()
    
    # Show usage instructions
    show_usage_instructions()

if __name__ == "__main__":
    main()
