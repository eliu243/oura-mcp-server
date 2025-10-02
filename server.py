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
        self._setup_tools()
        
    def _setup_tools(self):
        """Set up MCP tools."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="oura_auth",
                        description="Get OAuth2 authorization URL to connect your Oura Ring account",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "scope": {
                                    "type": "string",
                                    "description": "OAuth2 scopes to request (default: 'personal daily')",
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
                    ),
                    Tool(
                        name="oura_set_token",
                        description="Set access token directly (for testing or manual setup)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "access_token": {
                                    "type": "string",
                                    "description": "Oura API access token"
                                }
                            },
                            "required": ["access_token"]
                        }
                    ),
                    Tool(
                        name="oura_last_night_sleep",
                        description="Get sleep score from last night",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="oura_week_sleep",
                        description="Get sleep scores from the past week",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            
            if name == "oura_auth":
                return await self._handle_auth(arguments)
            elif name == "oura_exchange_code":
                return await self._handle_exchange_code(arguments)
            elif name == "oura_set_token":
                return await self._handle_set_token(arguments)
            elif name == "oura_last_night_sleep":
                return await self._handle_last_night_sleep(arguments)
            elif name == "oura_week_sleep":
                return await self._handle_week_sleep(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _handle_auth(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle OAuth2 authorization."""
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
                            text="Error: Oura API credentials not configured. Please set OURA_CLIENT_ID and OURA_CLIENT_SECRET environment variables."
                        )
                    ]
                )
            
            self.auth = OuraAuth(client_id, client_secret, redirect_uri)
        
        auth_url = self.auth.get_authorization_url(scope=scope)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Please visit this URL to authorize the application:\n{auth_url}\n\nAfter authorization, use the 'oura_exchange_code' tool with the code from the callback URL."
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
                        text="Error: Must call 'oura_auth' first to initialize authentication."
                    )
                ]
            )
        
        try:
            token_data = await self.auth.exchange_code_for_token(code)
            self.client = OuraClient(token_data["access_token"])
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Successfully authenticated! Access token expires in {token_data['expires_in']} seconds.\n\nYou can now use the sleep data tools."
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error exchanging code for token: {str(e)}"
                    )
                ]
            )
    
    async def _handle_set_token(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle setting access token directly."""
        access_token = arguments["access_token"]
        self.client = OuraClient(access_token)
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Access token set successfully. You can now use the sleep data tools."
                )
            ]
        )
    
    async def _handle_last_night_sleep(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle getting last night's sleep score."""
        if not self.client:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Error: Must authenticate first. Use 'oura_auth' and 'oura_exchange_code' tools, or 'oura_set_token' to set an access token."
                    )
                ]
            )
        
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
        if not self.client:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Error: Must authenticate first. Use 'oura_auth' and 'oura_exchange_code' tools, or 'oura_set_token' to set an access token."
                    )
                ]
            )
        
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
    oura_server = OuraMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await oura_server.server.run(
            read_stream,
            write_stream,
            oura_server.server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
