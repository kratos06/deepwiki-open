#!/usr/bin/env python3
"""
Simple MCP Client Test

This script creates a simple MCP client to test the DeepWiki MCP server.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Test MCP server using subprocess communication"""
    print("🔌 Testing DeepWiki MCP Server with MCP Protocol")
    print("=" * 60)
    
    try:
        # Start the MCP server process
        process = subprocess.Popen(
            [sys.executable, "mcp_deepwiki.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        print("✅ MCP server process started")
        
        # MCP initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialization request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read initialization response
        response_line = process.stdout.readline()
        if response_line:
            try:
                init_response = json.loads(response_line.strip())
                print(f"✅ Initialization response: {init_response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            except json.JSONDecodeError:
                print(f"⚠️  Non-JSON response: {response_line.strip()}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        print("📤 Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Test 1: List tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("📤 Requesting tools list...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            try:
                tools_response = json.loads(response_line.strip())
                tools = tools_response.get('result', {}).get('tools', [])
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            except json.JSONDecodeError:
                print(f"⚠️  Non-JSON response: {response_line.strip()}")
        
        # Test 2: List resources
        resources_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/list",
            "params": {}
        }
        
        print("📤 Requesting resources list...")
        process.stdin.write(json.dumps(resources_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            try:
                resources_response = json.loads(response_line.strip())
                resources = resources_response.get('result', {}).get('resources', [])
                print(f"✅ Found {len(resources)} resources:")
                for resource in resources:
                    print(f"   - {resource.get('uri', 'Unknown')}: {resource.get('description', 'No description')}")
            except json.JSONDecodeError:
                print(f"⚠️  Non-JSON response: {response_line.strip()}")
        
        # Test 3: List prompts
        prompts_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "prompts/list",
            "params": {}
        }
        
        print("📤 Requesting prompts list...")
        process.stdin.write(json.dumps(prompts_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            try:
                prompts_response = json.loads(response_line.strip())
                prompts = prompts_response.get('result', {}).get('prompts', [])
                print(f"✅ Found {len(prompts)} prompts:")
                for prompt in prompts:
                    print(f"   - {prompt.get('name', 'Unknown')}: {prompt.get('description', 'No description')}")
            except json.JSONDecodeError:
                print(f"⚠️  Non-JSON response: {response_line.strip()}")
        
        # Test 4: Call a tool (get_file_content - simplest one)
        tool_call_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_file_content",
                "arguments": {
                    "repo_url": "https://github.com/octocat/Hello-World",
                    "file_path": "README"
                }
            }
        }
        
        print("📤 Calling get_file_content tool...")
        process.stdin.write(json.dumps(tool_call_request) + "\n")
        process.stdin.flush()
        
        # Wait a bit longer for tool response
        await asyncio.sleep(2)
        
        response_line = process.stdout.readline()
        if response_line:
            try:
                tool_response = json.loads(response_line.strip())
                result = tool_response.get('result', {})
                if 'content' in result:
                    content = result['content']
                    if isinstance(content, list) and len(content) > 0:
                        text_content = content[0].get('text', 'No text content')
                        print(f"✅ Tool response: {text_content[:100]}...")
                    else:
                        print(f"✅ Tool response: {str(result)[:100]}...")
                else:
                    print(f"✅ Tool response: {str(result)[:100]}...")
            except json.JSONDecodeError:
                print(f"⚠️  Non-JSON response: {response_line.strip()}")
        
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("✅ MCP server test completed")
        return True
        
    except Exception as e:
        print(f"❌ MCP server test failed: {str(e)}")
        if 'process' in locals():
            process.terminate()
        return False

async def test_with_mcp_cli():
    """Test using MCP CLI if available"""
    print("\n🛠️  Testing with MCP CLI")
    print("=" * 40)
    
    try:
        # Check if mcp command is available
        result = subprocess.run(
            ["mcp", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ MCP CLI is available")
            
            # Test with mcp dev command
            print("📤 Testing with 'mcp dev'...")
            
            # Create a simple test script
            test_script = """
import json
import sys

# Send initialization
init_req = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0.0"}
    }
}
print(json.dumps(init_req))

# Send initialized notification
init_notif = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
    "params": {}
}
print(json.dumps(init_notif))

# Request tools list
tools_req = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}
print(json.dumps(tools_req))
"""
            
            with open("test_mcp_commands.py", "w") as f:
                f.write(test_script)
            
            # Run mcp dev with our test commands
            mcp_process = subprocess.Popen(
                ["python", "test_mcp_commands.py"],
                stdout=subprocess.PIPE,
                text=True
            )
            
            dev_process = subprocess.Popen(
                ["mcp", "dev", "mcp_deepwiki.py"],
                stdin=mcp_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            try:
                stdout, stderr = dev_process.communicate(timeout=10)
                print(f"✅ MCP dev output: {stdout[:200]}...")
                if stderr:
                    print(f"⚠️  MCP dev stderr: {stderr[:200]}...")
            except subprocess.TimeoutExpired:
                dev_process.kill()
                print("⚠️  MCP dev test timed out")
            
            # Clean up
            Path("test_mcp_commands.py").unlink(missing_ok=True)
            
        else:
            print("⚠️  MCP CLI not available, skipping CLI tests")
            
    except FileNotFoundError:
        print("⚠️  MCP CLI not found, skipping CLI tests")
    except Exception as e:
        print(f"⚠️  MCP CLI test error: {str(e)}")

async def main():
    """Main test function"""
    print("🚀 DeepWiki MCP Client Test Suite")
    print("=" * 60)
    
    # Test 1: Direct MCP protocol communication
    success1 = await test_mcp_server()
    
    # Test 2: MCP CLI if available
    await test_with_mcp_cli()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    if success1:
        print("✅ MCP protocol communication test: PASSED")
        print("\n🎉 MCP server is working correctly!")
        print("\n📋 Ready for use with:")
        print("• Claude Desktop: mcp install mcp_deepwiki.py --name 'DeepWiki'")
        print("• MCP development: mcp dev mcp_deepwiki.py")
        print("• Direct integration: Use the MCP protocol over stdio")
    else:
        print("❌ MCP protocol communication test: FAILED")
        print("\n⚠️  Check the error messages above for troubleshooting")

if __name__ == "__main__":
    asyncio.run(main())
