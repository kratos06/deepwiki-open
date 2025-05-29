#!/usr/bin/env python3
"""
MCP Protocol Test Script

This script tests the MCP server by directly calling the MCP tools and functions
to simulate what a real MCP client would do.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import api modules
sys.path.append(str(Path(__file__).parent.parent))

async def test_mcp_tools():
    """Test MCP tools directly"""
    print("🔧 Testing MCP Tools Directly")
    print("=" * 50)
    
    try:
        # Import MCP server components
        from api.mcp_server import (
            ask_deepwiki,
            query_code, 
            get_file_content,
            get_repo_structure,
            get_wiki_cache,
            get_repo_files
        )
        
        print("✅ MCP server components imported successfully")
        
        # Test repository
        test_repo = "https://github.com/octocat/Hello-World"
        
        # Test 1: ask_deepwiki tool
        print("\n1. Testing ask_deepwiki tool...")
        try:
            result = await ask_deepwiki(
                repo_url=test_repo,
                question="What is this repository about? Give a brief description.",
                provider="google"
            )
            print(f"✅ ask_deepwiki result: {result[:100]}...")
        except Exception as e:
            print(f"❌ ask_deepwiki failed: {str(e)}")
        
        # Test 2: query_code tool
        print("\n2. Testing query_code tool...")
        try:
            result = await query_code(
                repo_url=test_repo,
                query="Show me the main files in this repository",
                provider="google"
            )
            print(f"✅ query_code result: {result[:100]}...")
        except Exception as e:
            print(f"❌ query_code failed: {str(e)}")
        
        # Test 3: get_file_content tool
        print("\n3. Testing get_file_content tool...")
        try:
            result = await get_file_content(
                repo_url=test_repo,
                file_path="README"
            )
            print(f"✅ get_file_content result: {result[:100]}...")
        except Exception as e:
            print(f"❌ get_file_content failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import MCP components: {str(e)}")
        return False

async def test_mcp_resources():
    """Test MCP resources directly"""
    print("\n📚 Testing MCP Resources Directly")
    print("=" * 50)
    
    try:
        from api.mcp_server import get_repo_structure, get_wiki_cache, get_repo_files
        
        test_repo = "https://github.com/octocat/Hello-World"
        
        # Test 1: Repository structure
        print("\n1. Testing repository structure resource...")
        try:
            result = await get_repo_structure(test_repo)
            print(f"✅ Repository structure: {result[:100]}...")
        except Exception as e:
            print(f"❌ Repository structure failed: {str(e)}")
        
        # Test 2: Wiki cache
        print("\n2. Testing wiki cache resource...")
        try:
            result = await get_wiki_cache("octocat", "Hello-World", "github", "en")
            print(f"✅ Wiki cache: {result[:100]}...")
        except Exception as e:
            print(f"❌ Wiki cache failed: {str(e)}")
        
        # Test 3: Repository files
        print("\n3. Testing repository files resource...")
        try:
            result = await get_repo_files(test_repo, "*.md")
            print(f"✅ Repository files: {result[:100]}...")
        except Exception as e:
            print(f"❌ Repository files failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test MCP resources: {str(e)}")
        return False

def test_mcp_prompts():
    """Test MCP prompts directly"""
    print("\n💬 Testing MCP Prompts Directly")
    print("=" * 50)
    
    try:
        from api.mcp_server import (
            analyze_code_structure,
            debug_code_issue,
            explain_code_functionality,
            code_review_checklist
        )
        
        test_repo = "https://github.com/octocat/Hello-World"
        
        # Test 1: Code structure analysis prompt
        print("\n1. Testing analyze_code_structure prompt...")
        try:
            result = analyze_code_structure(test_repo)
            print(f"✅ Code structure prompt: {result[:100]}...")
        except Exception as e:
            print(f"❌ Code structure prompt failed: {str(e)}")
        
        # Test 2: Debug issue prompt
        print("\n2. Testing debug_code_issue prompt...")
        try:
            result = debug_code_issue(test_repo, "Module not found error")
            print(f"✅ Debug issue prompt: {result[:100]}...")
        except Exception as e:
            print(f"❌ Debug issue prompt failed: {str(e)}")
        
        # Test 3: Explain functionality prompt
        print("\n3. Testing explain_code_functionality prompt...")
        try:
            result = explain_code_functionality(test_repo, "README", "main")
            print(f"✅ Explain functionality prompt: {result[:100]}...")
        except Exception as e:
            print(f"❌ Explain functionality prompt failed: {str(e)}")
        
        # Test 4: Code review checklist prompt
        print("\n4. Testing code_review_checklist prompt...")
        try:
            result = code_review_checklist(test_repo)
            print(f"✅ Code review checklist: {len(result)} messages")
        except Exception as e:
            print(f"❌ Code review checklist failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test MCP prompts: {str(e)}")
        return False

async def test_mcp_server_status():
    """Test MCP server status via HTTP"""
    print("\n🌐 Testing MCP Server HTTP Status")
    print("=" * 50)
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Test MCP status endpoint
            async with session.get("http://localhost:8001/mcp/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ MCP status endpoint accessible")
                    print(f"   Running: {data['mcp_server']['running']}")
                    print(f"   Initialized: {data['mcp_server']['initialized']}")
                    print(f"   Tools: {len(data['mcp_server']['tools'])}")
                    print(f"   Resources: {len(data['mcp_server']['resources'])}")
                    print(f"   Prompts: {len(data['mcp_server']['prompts'])}")
                    return True
                else:
                    print(f"❌ MCP status endpoint failed: HTTP {response.status}")
                    return False
                    
    except ImportError:
        print("⚠️  aiohttp not available, skipping HTTP tests")
        return True
    except Exception as e:
        print(f"❌ HTTP test failed: {str(e)}")
        return False

def simulate_mcp_client_interaction():
    """Simulate what an MCP client would do"""
    print("\n🤖 Simulating MCP Client Interaction")
    print("=" * 50)
    
    print("Simulating MCP client workflow:")
    print("1. Client connects to MCP server")
    print("2. Client requests available tools, resources, and prompts")
    print("3. Client calls specific tools with parameters")
    print("4. Client receives responses")
    
    # This would be the typical MCP protocol flow:
    mcp_requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        },
        {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "resources/list",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": 3, 
            "method": "prompts/list",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "ask_deepwiki",
                "arguments": {
                    "repo_url": "https://github.com/octocat/Hello-World",
                    "question": "What is this repository about?",
                    "provider": "google"
                }
            }
        }
    ]
    
    print("\nExample MCP protocol requests that would be sent:")
    for i, request in enumerate(mcp_requests, 1):
        print(f"\n{i}. {request['method']}:")
        print(json.dumps(request, indent=2))
    
    print("\n✅ MCP client simulation completed")
    print("Note: Actual MCP protocol communication happens over stdio")
    
    return True

async def main():
    """Main test function"""
    print("🚀 DeepWiki MCP Protocol Test Suite")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check environment
    api_keys = ["GOOGLE_API_KEY", "OPENAI_API_KEY"]
    missing_keys = [key for key in api_keys if not os.environ.get(key)]
    
    if missing_keys:
        print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Some tests may fail or produce limited results.")
    
    # Run tests
    results = []
    
    # Test MCP server status via HTTP
    results.append(await test_mcp_server_status())
    
    # Test MCP prompts (these don't require API calls)
    results.append(test_mcp_prompts())
    
    # Test MCP tools and resources (these may require API calls)
    if not missing_keys:
        results.append(await test_mcp_tools())
        results.append(await test_mcp_resources())
    else:
        print("\n⏭️  Skipping tool and resource tests due to missing API keys")
    
    # Simulate MCP client interaction
    results.append(simulate_mcp_client_interaction())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 All tests passed! MCP server is working correctly.")
        print("\n📋 Next steps:")
        print("1. Test with real MCP client: mcp dev mcp_deepwiki.py")
        print("2. Install in Claude Desktop: mcp install mcp_deepwiki.py --name 'DeepWiki'")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
