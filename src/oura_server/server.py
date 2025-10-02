"""
Oura Ring OAuth2 MCP Server using FastMCP
"""

import os
import secrets
import urllib.parse
from typing import Any, Dict

import httpx
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field
from smithery.decorators import smithery


class ConfigSchema(BaseModel):
    client_id: str = Field(description="Oura API client ID")
    client_secret: str = Field(description="Oura API client secret")
    redirect_uri: str = Field(default="http://localhost:8080/callback", description="OAuth2 redirect URI")


@smithery.server(config_schema=ConfigSchema)
def create_server():
    """Create and return a FastMCP server instance with OAuth2 authentication."""
    
    server = FastMCP(name="Oura Ring OAuth2")

    @server.tool()
    def get_auth_url(ctx: Context, scope: str = "personal daily") -> str:
        """Get OAuth2 authorization URL to connect your Oura Ring account."""
        config = ctx.session_config
        
        if not config.client_id or not config.client_secret:
            return "❌ Error: Oura API credentials not configured. Please set client_id and client_secret in your session configuration."
        
        state = secrets.token_urlsafe(32)
        params = {
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": scope,
            "state": state
        }
        
        auth_url = f"https://cloud.ouraring.com/oauth/authorize?{urllib.parse.urlencode(params)}"
        
        return f"🔗 OAuth2 Authorization URL:\n\n{auth_url}\n\nVisit this URL to authorize the application, then use the 'exchange_code' tool with the code from the callback URL."

    @server.tool()
    def exchange_code(code: str, ctx: Context) -> str:
        """Exchange authorization code for access token."""
        config = ctx.session_config
        
        if not config.client_id or not config.client_secret:
            return "❌ Error: Oura API credentials not configured. Please set client_id and client_secret in your session configuration."
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.redirect_uri,
            "client_id": config.client_id,
            "client_secret": config.client_secret
        }
        
        try:
            response = httpx.post(
                "https://api.ouraring.com/oauth/token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token_data = response.json()
            
            return f"✅ Successfully authenticated with Oura Ring!\n\nAccess Token: {token_data['access_token'][:20]}...\nExpires in: {token_data['expires_in']} seconds\nToken Type: {token_data['token_type']}\n\nYou can now use this access token to make API calls to Oura."
            
        except Exception as e:
            return f"❌ Error exchanging code for token: {str(e)}"

    return server
