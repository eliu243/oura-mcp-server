#!/usr/bin/env python3
"""
Simple Oura Ring MCP Server - OAuth2 Authentication Only
"""

import asyncio
import json
import os
import secrets
import urllib.parse
from typing import Any, Dict

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)


class OuraAuth:
    """Simple OAuth2 authentication with Oura API."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorize_url = "https://cloud.ouraring.com/oauth/authorize"
        self.token_url = "https://api.ouraring.com/oauth/token"
    
    def get_authorization_url(self, scope: str = "personal daily") -> str:
        """Generate authorization URL for OAuth2 flow."""
        state = secrets.token_urlsafe(32)
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "state": state
        }
        return f"{self.authorize_url}?{urllib.parse.urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()


class OuraMCPServer:
    """Simple MCP Server for Oura Ring OAuth2."""
    
    def __init__(self):
        self.server = Server("oura-auth")
        self.auth = None
        self._setup_tools()
        
    def _setup_tools(self):
        """Set up MCP tools."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="oura_get_auth_url",
                        description="Get OAuth2 authorization URL to connect your Oura Ring account",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "scope": {
                                    "type": "string",
                                    "description": "OAuth2 scopes (default: 'personal daily')",
                                    "default": "personal daily"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="oura_exchange_code",
                        description="Exchange authorization code for access token",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "description": "Authorization code from OAuth2 callback"
                                }
                            },
                            "required": ["code"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            
            if name == "oura_get_auth_url":
                return await self._handle_get_auth_url(arguments)
            elif name == "oura_exchange_code":
                return await self._handle_exchange_code(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _handle_get_auth_url(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle getting authorization URL."""
        scope = arguments.get("scope", "personal daily")
        
        # Initialize auth if not already done
        if not self.auth:
            client_id = os.getenv("OURA_CLIENT_ID")
            client_secret = os.getenv("OURA_CLIENT_SECRET")
            redirect_uri = os.getenv("OURA_REDIRECT_URI", "http://localhost:8080/callback")
            
            if not client_id or not client_secret:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="❌ Error: Oura API credentials not configured. Please set OURA_CLIENT_ID and OURA_CLIENT_SECRET environment variables."
                        )
                    ]
                )
            
            self.auth = OuraAuth(client_id, client_secret, redirect_uri)
        
        auth_url = self.auth.get_authorization_url(scope=scope)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"🔗 OAuth2 Authorization URL:\n\n{auth_url}\n\nVisit this URL to authorize the application, then use the 'oura_exchange_code' tool with the code from the callback URL."
                )
            ]
        )
    
    async def _handle_exchange_code(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle code exchange for access token."""
        code = arguments["code"]
        
        if not self.auth:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="❌ Error: Must call 'oura_get_auth_url' first to initialize authentication."
                    )
                ]
            )
        
        try:
            token_data = await self.auth.exchange_code_for_token(code)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"✅ Successfully authenticated with Oura Ring!\n\nAccess Token: {token_data['access_token'][:20]}...\nExpires in: {token_data['expires_in']} seconds\nToken Type: {token_data['token_type']}\n\nYou can now use this access token to make API calls to Oura."
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Error exchanging code for token: {str(e)}"
                    )
                ]
            )


async def main():
    """Main entry point."""
    oura_server = OuraMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await oura_server.server.run(
            read_stream,
            write_stream,
            oura_server.server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())