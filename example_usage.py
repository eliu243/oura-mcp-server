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
    
    # Example 1: Simple authentication setup
    print("\n1️⃣ Simple Authentication Setup")
    print("-" * 30)
    print("🔐 One-time setup with your Oura access token:")
    print("   await server._handle_setup_auth({'access_token': 'your_token_here'})")
    print("\n💡 Get your token from: https://cloud.ouraring.com/oauth/applications")
    
    # Example 2: Automatic sleep data retrieval
    print("\n\n2️⃣ Automatic Sleep Data Retrieval")
    print("-" * 30)
    print("😴 Just ask for your sleep data - authentication is automatic:")
    print("   • Last night: await server._handle_last_night_sleep({})")
    print("   • Past week: await server._handle_week_sleep({})")
    print("\n✨ No more manual auth steps needed!")
    
    # Example 3: Available tools
    print("\n\n3️⃣ Available MCP Tools")
    print("-" * 30)
    tools = [
        ("oura_setup_auth", "One-time authentication setup"),
        ("oura_last_night_sleep", "Get last night's sleep data"),
        ("oura_week_sleep", "Get past week's sleep scores")
    ]
    
    for tool_name, description in tools:
        print(f"   🔧 {tool_name}: {description}")
    
    print("\n✨ Example completed!")
    print("\n📚 For more information, see README.md")


if __name__ == "__main__":
    asyncio.run(example_usage())
