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
    
    # Test 1: Test authentication check
    print("\n1. Testing authentication check...")
    sleep_result = await server._handle_last_night_sleep({})
    print("Authentication check completed:")
    print(sleep_result.content[0].text)
    
    # Test 2: Test setup auth tool
    print("\n2. Testing setup auth tool...")
    setup_result = await server._handle_setup_auth({"access_token": "invalid_token"})
    print("Setup auth test completed:")
    print(setup_result.content[0].text)
    
    # Test 3: Test week sleep data (should show auth required)
    print("\n3. Testing week sleep data...")
    week_result = await server._handle_week_sleep({})
    print("Week sleep test completed:")
    print(week_result.content[0].text)
    
    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(test_server())
