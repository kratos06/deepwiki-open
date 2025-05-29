#!/usr/bin/env python3
"""
Integration test for DeepWiki with MCP Server

This script tests the complete integration of DeepWiki with MCP server functionality.
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# Add parent directory to path so we can import api modules
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_service_integration():
    """Test MCP service integration with FastAPI"""
    print("🔧 Testing MCP Service Integration...")
    
    try:
        # Test MCP service manager
        from api.mcp_service import mcp_service, get_mcp_status
        
        print("✅ MCP service manager imported successfully")
        
        # Test initialization
        success = await mcp_service.start_mcp_server()
        if success:
            print("✅ MCP server components initialized successfully")
        else:
            print("❌ MCP server initialization failed")
            return False
        
        # Test status
        status = await get_mcp_status()
        print(f"✅ MCP status retrieved: {status['mcp_server']['status']}")
        
        # Test stop
        await mcp_service.stop_mcp_server()
        print("✅ MCP server stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP service integration test failed: {str(e)}")
        return False

async def test_fastapi_integration():
    """Test FastAPI app with MCP integration"""
    print("\n🌐 Testing FastAPI Integration...")
    
    try:
        # Import FastAPI app
        from api.api import app
        
        print("✅ FastAPI app with MCP integration loaded successfully")
        
        # Test if MCP service is available in app state
        if hasattr(app, 'state'):
            print("✅ App state available for MCP integration")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI integration test failed: {str(e)}")
        return False

def test_startup_script():
    """Test the startup script"""
    print("\n🚀 Testing Startup Script...")
    
    try:
        # Import startup script
        import start_deepwiki
        
        print("✅ Startup script imported successfully")
        
        # Test launcher creation
        launcher = start_deepwiki.DeepWikiLauncher()
        print("✅ DeepWiki launcher created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Startup script test failed: {str(e)}")
        return False

def test_mcp_server_standalone():
    """Test standalone MCP server"""
    print("\n🔌 Testing Standalone MCP Server...")
    
    try:
        # Import MCP server
        from api.mcp_server import mcp
        
        print("✅ MCP server imported successfully")
        
        # Test MCP server components
        if hasattr(mcp, '_tools') or hasattr(mcp, 'tools'):
            print("✅ MCP tools available")
        
        return True
        
    except Exception as e:
        print(f"❌ Standalone MCP server test failed: {str(e)}")
        return False

def check_environment():
    """Check environment setup"""
    print("🔍 Checking Environment...")
    
    # Check required files
    required_files = [
        "api/main.py",
        "api/api.py", 
        "api/mcp_server.py",
        "api/mcp_service.py",
        "mcp_deepwiki.py",
        "start_deepwiki.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
    
    # Check environment variables
    api_keys = ["GOOGLE_API_KEY", "OPENAI_API_KEY"]
    missing_keys = [key for key in api_keys if not os.environ.get(key)]
    
    if missing_keys:
        print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Some functionality may be limited")
    else:
        print("✅ API keys configured")
    
    return True

async def main():
    """Main test function"""
    print("🧪 DeepWiki MCP Integration Test Suite")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed")
        return False
    
    # Run tests
    tests = [
        ("MCP Service Integration", test_mcp_service_integration()),
        ("FastAPI Integration", test_fastapi_integration()),
        ("Startup Script", test_startup_script()),
        ("Standalone MCP Server", test_mcp_server_standalone())
    ]
    
    results = []
    for test_name, test_coro in tests:
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! DeepWiki MCP integration is working correctly.")
        print("\n📋 Next steps:")
        print("1. Start DeepWiki with MCP integration:")
        print("   python start_deepwiki.py")
        print("\n2. Install in Claude Desktop:")
        print("   mcp install mcp_deepwiki.py --name 'DeepWiki Code Assistant'")
        print("\n3. Test MCP functionality:")
        print("   mcp dev mcp_deepwiki.py")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
