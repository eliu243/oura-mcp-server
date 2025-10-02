#!/usr/bin/env python3
"""
Example usage of the Oura MCP Server.
This demonstrates how to interact with the server programmatically.
"""

import asyncio
import os
from server import OuraMCPServer


async def example_usage():
    """Example of using the Oura MCP Server."""
    print("🔮 Oura MCP Server - Example Usage")
    print("=" * 50)
    
    # Create server instance
    server = OuraMCPServer()
    
    # Example 1: Authentication flow
    print("\n1️⃣ Authentication Flow")
    print("-" * 30)
    
    if os.getenv("OURA_CLIENT_ID"):
        print("✅ Oura credentials found in environment")
        
        # Get authorization URL
        auth_result = await server._handle_auth({"scope": "personal daily"})
        print("📋 Authorization URL generated:")
        print(auth_result.content[0].text)
        
        print("\n💡 Next steps:")
        print("   1. Visit the URL above to authorize")
        print("   2. Copy the 'code' parameter from the callback")
        print("   3. Use 'oura_exchange_code' tool with the code")
        
    else:
        print("❌ No Oura credentials found")
        print("   Set OURA_CLIENT_ID and OURA_CLIENT_SECRET environment variables")
        print("   Or use 'oura_set_token' to set an access token directly")
    
    # Example 2: Direct token usage (for testing)
    print("\n\n2️⃣ Direct Token Usage")
    print("-" * 30)
    print("For testing, you can set a token directly:")
    print("   await server._handle_set_token({'access_token': 'your_token_here'})")
    
    # Example 3: Sleep data retrieval
    print("\n\n3️⃣ Sleep Data Retrieval")
    print("-" * 30)
    print("Once authenticated, you can get sleep data:")
    print("   • Last night: await server._handle_last_night_sleep({})")
    print("   • Past week: await server._handle_week_sleep({})")
    
    # Example 4: Available tools
    print("\n\n4️⃣ Available MCP Tools")
    print("-" * 30)
    tools = [
        ("oura_auth", "Get OAuth2 authorization URL"),
        ("oura_exchange_code", "Exchange code for access token"),
        ("oura_set_token", "Set access token directly"),
        ("oura_last_night_sleep", "Get last night's sleep data"),
        ("oura_week_sleep", "Get past week's sleep scores")
    ]
    
    for tool_name, description in tools:
        print(f"   🔧 {tool_name}: {description}")
    
    print("\n✨ Example completed!")
    print("\n📚 For more information, see README.md")


if __name__ == "__main__":
    asyncio.run(example_usage())
