#!/usr/bin/env python3
"""
Oura Ring MCP Server

This server provides access to Oura Ring sleep data through MCP (Model Context Protocol).
It implements OAuth2 authentication and provides tools to fetch sleep scores.
"""

import asyncio
import json
import os
import secrets
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)


class OuraAuth:
    """Handles OAuth2 authentication with Oura API."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorize_url = "https://cloud.ouraring.com/oauth/authorize"
        self.token_url = "https://api.ouraring.com/oauth/token"
        self.revoke_url = "https://api.ouraring.com/oauth/revoke"
        
    def get_authorization_url(self, state: Optional[str] = None, scope: str = "personal daily") -> str:
        """Generate authorization URL for OAuth2 flow."""
        if state is None:
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
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
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


class OuraClient:
    """Client for interacting with Oura API."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.ouraring.com/v2"
        
    async def get_sleep_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Fetch sleep data from Oura API."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/usercollection/sleep",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()


class OuraMCPServer:
    """MCP Server for Oura Ring data."""
    
    def __init__(self):
        self.server = Server("oura-ring")
        self.auth = None
        self.client = None
        self._token_file = os.path.expanduser("~/.oura_token")
        self._setup_tools()
        self._load_saved_token()
    
    def _load_saved_token(self):
        """Load saved access token from file."""
        try:
            if os.path.exists(self._token_file):
                with open(self._token_file, 'r') as f:
                    token_data = json.load(f)
                    if token_data.get('access_token'):
                        self.client = OuraClient(token_data['access_token'])
                        print(f"✅ Loaded saved Oura token (expires: {token_data.get('expires_at', 'unknown')})")
        except Exception as e:
            print(f"⚠️ Could not load saved token: {e}")
    
    def _save_token(self, token_data):
        """Save access token to file."""
        try:
            token_data['expires_at'] = datetime.now() + timedelta(seconds=token_data.get('expires_in', 2592000))
            with open(self._token_file, 'w') as f:
                json.dump(token_data, f)
            print(f"💾 Saved Oura token to {self._token_file}")
        except Exception as e:
            print(f"⚠️ Could not save token: {e}")
        
    def _setup_tools(self):
        """Set up MCP tools."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="oura_last_night_sleep",
                        description="Get sleep score and detailed data from last night",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="oura_week_sleep",
                        description="Get sleep scores and trends from the past week",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="oura_setup_auth",
                        description="Set up Oura Ring authentication (one-time setup)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "access_token": {
                                    "type": "string",
                                    "description": "Oura API access token from https://cloud.ouraring.com/oauth/applications"
                                }
                            },
                            "required": ["access_token"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            
            if name == "oura_setup_auth":
                return await self._handle_setup_auth(arguments)
            elif name == "oura_last_night_sleep":
                return await self._handle_last_night_sleep(arguments)
            elif name == "oura_week_sleep":
                return await self._handle_week_sleep(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _handle_setup_auth(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle one-time authentication setup."""
        access_token = arguments["access_token"]
        
        try:
            # Test the token by making a simple API call
            test_client = OuraClient(access_token)
            await test_client.get_sleep_data()
            
            # If successful, save the token
            token_data = {
                "access_token": access_token,
                "expires_in": 2592000,  # 30 days default
                "setup_date": datetime.now().isoformat()
            }
            self._save_token(token_data)
            self.client = test_client
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="✅ Oura Ring authentication set up successfully! Your access token has been saved and you can now access your sleep data."
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Failed to authenticate with Oura Ring: {str(e)}\n\nPlease check your access token and try again. You can get a new token from https://cloud.ouraring.com/oauth/applications"
                    )
                ]
            )
    
    async def _ensure_authenticated(self) -> CallToolResult:
        """Ensure user is authenticated, show setup instructions if not."""
        if not self.client:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="🔐 Oura Ring authentication required!\n\nTo get your sleep data, you need to set up authentication first:\n\n1. Go to https://cloud.ouraring.com/oauth/applications\n2. Create an application and get an access token\n3. Use the 'oura_setup_auth' tool with your access token\n\nThis is a one-time setup - your token will be saved for future use."
                    )
                ]
            )
        return None
    
    async def _handle_last_night_sleep(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle getting last night's sleep score."""
        # Check authentication
        auth_error = await self._ensure_authenticated()
        if auth_error:
            return auth_error
        
        try:
            # Get yesterday's date
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            sleep_data = await self.client.get_sleep_data(start_date=yesterday, end_date=yesterday)
            
            if not sleep_data.get("data"):
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"No sleep data available for {yesterday}."
                        )
                    ]
                )
            
            # Get the most recent sleep record
            latest_sleep = sleep_data["data"][0]
            
            result = {
                "date": latest_sleep.get("day"),
                "sleep_score": latest_sleep.get("score"),
                "sleep_efficiency": latest_sleep.get("efficiency"),
                "rem_sleep_duration": latest_sleep.get("rem"),
                "deep_sleep_duration": latest_sleep.get("deep"),
                "light_sleep_duration": latest_sleep.get("light"),
                "total_sleep_duration": latest_sleep.get("total"),
                "bedtime_start": latest_sleep.get("bedtime_start"),
                "bedtime_end": latest_sleep.get("bedtime_end"),
                "sleep_latency": latest_sleep.get("latency"),
                "time_in_bed": latest_sleep.get("time_in_bed")
            }
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Last Night's Sleep Data ({result['date']}):\n"
                             f"Sleep Score: {result['sleep_score']}\n"
                             f"Sleep Efficiency: {result['sleep_efficiency']}%\n"
                             f"Total Sleep: {result['total_sleep_duration']} seconds\n"
                             f"REM Sleep: {result['rem_sleep_duration']} seconds\n"
                             f"Deep Sleep: {result['deep_sleep_duration']} seconds\n"
                             f"Light Sleep: {result['light_sleep_duration']} seconds\n"
                             f"Bedtime: {result['bedtime_start']} - {result['bedtime_end']}\n"
                             f"Sleep Latency: {result['sleep_latency']} seconds\n"
                             f"Time in Bed: {result['time_in_bed']} seconds"
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error fetching sleep data: {str(e)}"
                    )
                ]
            )
    
    async def _handle_week_sleep(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle getting past week's sleep scores."""
        # Check authentication
        auth_error = await self._ensure_authenticated()
        if auth_error:
            return auth_error
        
        try:
            # Get past week's date range
            end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
            
            sleep_data = await self.client.get_sleep_data(start_date=start_date, end_date=end_date)
            
            if not sleep_data.get("data"):
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"No sleep data available for the past week ({start_date} to {end_date})."
                        )
                    ]
                )
            
            # Process sleep data for the week
            sleep_records = sleep_data["data"]
            sleep_records.sort(key=lambda x: x.get("day", ""), reverse=True)  # Sort by date, newest first
            
            result_text = "Past Week's Sleep Scores:\n\n"
            
            for record in sleep_records:
                date = record.get("day", "Unknown")
                score = record.get("score", "N/A")
                efficiency = record.get("efficiency", "N/A")
                total_sleep = record.get("total", "N/A")
                
                result_text += f"{date}: Score {score}, Efficiency {efficiency}%, Total Sleep {total_sleep}s\n"
            
            # Calculate average score
            scores = [record.get("score") for record in sleep_records if record.get("score") is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
                result_text += f"\nAverage Sleep Score: {avg_score:.1f}"
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=result_text
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error fetching sleep data: {str(e)}"
                    )
                ]
            )


async def main():
    """Main entry point."""
    # Check if we should run as HTTP server (for health checks)
    if os.getenv("RUN_HTTP_SERVER") == "true":
        from fastapi import FastAPI
        import uvicorn
        
        app = FastAPI()
        
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "oura-mcp"}
        
        print("🌐 Starting HTTP server for health checks...")
        uvicorn.run(app, host="0.0.0.0", port=8080)
    else:
        # Run as MCP server
        oura_server = OuraMCPServer()
        
        async with stdio_server() as (read_stream, write_stream):
            await oura_server.server.run(
                read_stream,
                write_stream,
                oura_server.server.create_initialization_options()
            )


if __name__ == "__main__":
    asyncio.run(main())
