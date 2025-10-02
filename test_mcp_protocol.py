#!/usr/bin/env python3
"""
Test script to verify the MCP server works properly with the MCP protocol.
This simulates how Claude Desktop would interact with the server.
"""

import asyncio
import json
import subprocess
import sys
from mcp.server.stdio import stdio_server


async def test_mcp_protocol():
    """Test the MCP protocol interaction."""
    print("🧪 Testing MCP Protocol")
    print("=" * 40)
    
    # Test 1: Check if server can start
    print("\n1️⃣ Testing server startup...")
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, "server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        await asyncio.sleep(1)
        
        if process.poll() is None:
            print("✅ Server started successfully")
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start: {stderr}")
            return
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return
    
    # Test 2: Send MCP initialization
    print("\n2️⃣ Testing MCP initialization...")
    try:
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send initialization message
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()
        
        # Wait for response
        response = process.stdout.readline()
        if response:
            response_data = json.loads(response)
            if "result" in response_data:
                print("✅ MCP initialization successful")
            else:
                print(f"❌ MCP initialization failed: {response_data}")
        else:
            print("❌ No response from server")
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
    
    # Test 3: List tools
    print("\n3️⃣ Testing tool listing...")
    try:
        tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        process.stdin.write(json.dumps(tools_message) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            response_data = json.loads(response)
            if "result" in response_data and "tools" in response_data["result"]:
                tools = response_data["result"]["tools"]
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   🔧 {tool['name']}: {tool['description']}")
            else:
                print(f"❌ Tool listing failed: {response_data}")
        else:
            print("❌ No response from server")
            
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
    
    # Cleanup
    process.terminate()
    process.wait()
    
    print("\n🎉 MCP protocol test completed!")
    print("\n💡 If all tests passed, your server is ready for Claude Desktop!")


if __name__ == "__main__":
    asyncio.run(test_mcp_protocol())
