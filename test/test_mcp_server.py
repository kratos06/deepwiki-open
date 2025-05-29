#!/usr/bin/env python3
"""
Test script for DeepWiki MCP Server

This script tests the MCP server functionality to ensure all tools,
resources, and prompts are working correctly.

Usage:
    python test_mcp_server.py
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add the parent directory to the path so we can import api modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.mcp_server import (
    ask_deepwiki,
    query_code,
    get_file_content,
    get_repo_structure,
    get_wiki_cache,
    get_repo_files,
    analyze_code_structure,
    debug_code_issue,
    explain_code_functionality,
    code_review_checklist
)

async def test_tools():
    """Test MCP tools"""
    print("🔧 Testing MCP Tools...")
    
    # Test repository URL (using a small public repo for testing)
    test_repo = "https://github.com/octocat/Hello-World"
    
    try:
        print("\n1. Testing ask_deepwiki tool...")
        result = await ask_deepwiki(
            repo_url=test_repo,
            question="What is this repository about?",
            provider="google"
        )
        print(f"✅ ask_deepwiki result: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ ask_deepwiki failed: {str(e)}")
    
    try:
        print("\n2. Testing query_code tool...")
        result = await query_code(
            repo_url=test_repo,
            query="Show me the main files in this repository",
            provider="google"
        )
        print(f"✅ query_code result: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ query_code failed: {str(e)}")
    
    try:
        print("\n3. Testing get_file_content tool...")
        result = await get_file_content(
            repo_url=test_repo,
            file_path="README"
        )
        print(f"✅ get_file_content result: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ get_file_content failed: {str(e)}")

async def test_resources():
    """Test MCP resources"""
    print("\n📚 Testing MCP Resources...")
    
    test_repo = "https://github.com/octocat/Hello-World"
    
    try:
        print("\n1. Testing repo structure resource...")
        result = await get_repo_structure(test_repo)
        print(f"✅ repo structure result: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ repo structure failed: {str(e)}")
    
    try:
        print("\n2. Testing repo files resource...")
        result = await get_repo_files(test_repo)
        print(f"✅ repo files result: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ repo files failed: {str(e)}")
    
    try:
        print("\n3. Testing wiki cache resource...")
        result = await get_wiki_cache("octocat", "Hello-World", "github", "en")
        print(f"✅ wiki cache result: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ wiki cache failed: {str(e)}")

def test_prompts():
    """Test MCP prompts"""
    print("\n💬 Testing MCP Prompts...")
    
    test_repo = "https://github.com/octocat/Hello-World"
    
    try:
        print("\n1. Testing analyze_code_structure prompt...")
        result = analyze_code_structure(test_repo)
        print(f"✅ analyze_code_structure prompt: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ analyze_code_structure failed: {str(e)}")
    
    try:
        print("\n2. Testing debug_code_issue prompt...")
        result = debug_code_issue(test_repo, "Module not found error")
        print(f"✅ debug_code_issue prompt: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ debug_code_issue failed: {str(e)}")
    
    try:
        print("\n3. Testing explain_code_functionality prompt...")
        result = explain_code_functionality(test_repo, "README", "main")
        print(f"✅ explain_code_functionality prompt: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ explain_code_functionality failed: {str(e)}")
    
    try:
        print("\n4. Testing code_review_checklist prompt...")
        result = code_review_checklist(test_repo)
        print(f"✅ code_review_checklist prompt: {len(result)} messages")
        
    except Exception as e:
        print(f"❌ code_review_checklist failed: {str(e)}")

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking Environment...")
    
    required_vars = ["GOOGLE_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Some tests may fail without proper API keys.")
    else:
        print("✅ All required environment variables are set")
    
    return len(missing_vars) == 0

async def main():
    """Main test function"""
    print("🚀 DeepWiki MCP Server Test Suite")
    print("=" * 50)
    
    # Check environment
    env_ok = check_environment()
    
    if not env_ok:
        print("\n⚠️  Warning: Some environment variables are missing.")
        print("Tests may fail or produce limited results.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    print("\n" + "=" * 50)
    
    # Test prompts (these don't require API calls)
    test_prompts()
    
    # Test resources and tools (these may require API calls)
    if env_ok:
        await test_resources()
        await test_tools()
    else:
        print("\n⏭️  Skipping resource and tool tests due to missing API keys")
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\nTo run the MCP server:")
    print("  python mcp_deepwiki.py")
    print("\nTo install in Claude Desktop:")
    print("  mcp install mcp_deepwiki.py --name 'DeepWiki Code Assistant'")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    asyncio.run(main())
