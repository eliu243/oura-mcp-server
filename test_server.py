#!/usr/bin/env python3
"""
Simple test script for the Oura MCP Server.
This script demonstrates how to use the server programmatically.
"""

import asyncio
import os
from server import OuraMCPServer


async def test_server():
    """Test the Oura MCP Server functionality."""
    print("Testing Oura MCP Server...")
    
    # Create server instance
    server = OuraMCPServer()
    
    # Test 1: Test auth URL generation (if credentials are available)
    print("\n1. Testing authentication...")
    if os.getenv("OURA_CLIENT_ID"):
        auth_result = await server._handle_auth({"scope": "personal daily"})
        print("Auth URL generated successfully")
        print(auth_result.content[0].text[:100] + "...")
    else:
        print("Skipping auth test - no credentials found")
        print("Set OURA_CLIENT_ID and OURA_CLIENT_SECRET to test authentication")
    
    # Test 2: Test with invalid token
    print("\n2. Testing sleep data with invalid token...")
    server.client = server.client or type('MockClient', (), {
        'access_token': 'invalid_token'
    })()
    
    sleep_result = await server._handle_last_night_sleep({})
    print("Last night sleep test completed")
    print(sleep_result.content[0].text)
    
    # Test 3: Test week sleep data
    print("\n3. Testing week sleep data...")
    week_result = await server._handle_week_sleep({})
    print("Week sleep test completed")
    print(week_result.content[0].text)
    
    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(test_server())
