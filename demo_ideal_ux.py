#!/usr/bin/env python3
"""
Demo of the ideal user experience with the Oura MCP Server.
This shows how a user would interact with Claude Desktop.
"""

import asyncio
from server import OuraMCPServer


async def demo_ideal_ux():
    """Demonstrate the ideal user experience."""
    print("🎯 IDEAL USER EXPERIENCE DEMO")
    print("=" * 50)
    print("This shows how a user would interact with Claude Desktop:")
    print()
    
    # Create server instance
    server = OuraMCPServer()
    
    # Simulate user asking for sleep data (first time - no auth)
    print("👤 User: 'What was my sleep score last night?'")
    print("🤖 Claude: Let me check your Oura Ring data...")
    
    result1 = await server._handle_last_night_sleep({})
    print(f"📱 Server Response: {result1.content[0].text}")
    print()
    
    # Simulate user setting up auth
    print("👤 User: 'Let me set up my Oura account...'")
    print("🤖 Claude: I'll help you set up authentication.")
    print("👤 User: 'Here's my access token: your_oura_token_here'")
    
    # Note: In real usage, this would be a valid token
    print("🤖 Claude: Setting up authentication...")
    print("📱 Server Response: [Would test token and save it]")
    print()
    
    # Simulate user asking again (now authenticated)
    print("👤 User: 'Now what was my sleep score last night?'")
    print("🤖 Claude: Let me check your Oura Ring data...")
    
    # This would work with a real token
    print("📱 Server Response: [Would return actual sleep data]")
    print()
    
    print("✨ KEY IMPROVEMENTS:")
    print("   • Only 3 simple tools instead of 5 complex ones")
    print("   • One-time authentication setup")
    print("   • Automatic token persistence")
    print("   • Clear error messages with setup instructions")
    print("   • No more manual OAuth2 flow management")
    print()
    print("🎉 Much better user experience!")


if __name__ == "__main__":
    asyncio.run(demo_ideal_ux())
