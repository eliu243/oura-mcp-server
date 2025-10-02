"""
Oura Ring OAuth2 MCP Server using FastMCP
"""

import os
import secrets
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict

import httpx
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field
from smithery.decorators import smithery


class ConfigSchema(BaseModel):
    client_id: str = Field(description="Oura API client ID")
    client_secret: str = Field(description="Oura API client secret")
    redirect_uri: str = Field(default="http://localhost:8080/callback", description="OAuth2 redirect URI")
    access_token: str = Field(default="", description="Oura API access token")


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

    @server.tool()
    def parse_redirect_url(url: str, ctx: Context) -> str:
        """Parse OAuth2 redirect URL and automatically extract token/code."""
        try:
            # Try to extract access token from URL fragment (implicit flow)
            if "#" in url:
                fragment = url.split("#")[1]
                params = urllib.parse.parse_qs(fragment)
                if "access_token" in params:
                    token = params["access_token"][0]
                    expires_in = params.get("expires_in", ["unknown"])[0]
                    return f"✅ Access token found in URL!\n\nToken: {token[:20]}...\nExpires: {expires_in} seconds\n\nYou can now use this token for API calls."
            
            # Try to extract authorization code (authorization code flow)
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            
            if "code" in params:
                code = params["code"][0]
                # Automatically exchange the code for a token
                return exchange_code(code, ctx)
                
            return "❌ No access token or authorization code found in URL"
        except Exception as e:
            return f"❌ Error parsing URL: {str(e)}"

    @server.tool()
    def get_sleep_last_night(ctx: Context) -> str:
        """Get sleep data from last night."""
        config = ctx.session_config
        
        if not config.access_token:
            return "❌ Error: No access token found. Please complete OAuth2 authentication first."
        
        try:
            # Get yesterday's date
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            response = httpx.get(
                f"https://api.ouraring.com/v2/usercollection/sleep",
                headers={"Authorization": f"Bearer {config.access_token}"},
                params={"start_date": yesterday, "end_date": yesterday}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("data"):
                return f"❌ No sleep data found for {yesterday}"
            
            sleep = data["data"][0]
            
            return f"""😴 Sleep Data - {yesterday}

Sleep Score: {sleep.get('score', 'N/A')}
Sleep Efficiency: {sleep.get('efficiency', 'N/A')}%
Total Sleep: {sleep.get('total', 'N/A')} seconds
REM Sleep: {sleep.get('rem', 'N/A')} seconds
Deep Sleep: {sleep.get('deep', 'N/A')} seconds
Light Sleep: {sleep.get('light', 'N/A')} seconds
Bedtime: {sleep.get('bedtime_start', 'N/A')} - {sleep.get('bedtime_end', 'N/A')}
Sleep Latency: {sleep.get('latency', 'N/A')} seconds
Time in Bed: {sleep.get('time_in_bed', 'N/A')} seconds"""
            
        except Exception as e:
            return f"❌ Error fetching sleep data: {str(e)}"

    @server.tool()
    def get_sleep_last_week(ctx: Context) -> str:
        """Get sleep data from the past week."""
        config = ctx.session_config
        
        if not config.access_token:
            return "❌ Error: No access token found. Please complete OAuth2 authentication first."
        
        try:
            # Get past week's date range
            end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
            
            response = httpx.get(
                f"https://api.ouraring.com/v2/usercollection/sleep",
                headers={"Authorization": f"Bearer {config.access_token}"},
                params={"start_date": start_date, "end_date": end_date}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("data"):
                return f"❌ No sleep data found for {start_date} to {end_date}"
            
            sleep_records = data["data"]
            sleep_records.sort(key=lambda x: x.get("day", ""), reverse=True)
            
            result = f"😴 Sleep Data - Past Week ({start_date} to {end_date})\n\n"
            
            for record in sleep_records:
                date = record.get("day", "Unknown")
                score = record.get("score", "N/A")
                efficiency = record.get("efficiency", "N/A")
                total_sleep = record.get("total", "N/A")
                
                result += f"{date}: Score {score}, Efficiency {efficiency}%, Total Sleep {total_sleep}s\n"
            
            # Calculate average score
            scores = [record.get("score") for record in sleep_records if record.get("score") is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
                result += f"\nAverage Sleep Score: {avg_score:.1f}"
            
            return result
            
        except Exception as e:
            return f"❌ Error fetching sleep data: {str(e)}"

    @server.tool()
    def get_sleep_by_date(date: str, ctx: Context) -> str:
        """Get sleep data for a specific date (YYYY-MM-DD format)."""
        config = ctx.session_config
        
        if not config.access_token:
            return "❌ Error: No access token found. Please complete OAuth2 authentication first."
        
        try:
            response = httpx.get(
                f"https://api.ouraring.com/v2/usercollection/sleep",
                headers={"Authorization": f"Bearer {config.access_token}"},
                params={"start_date": date, "end_date": date}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("data"):
                return f"❌ No sleep data found for {date}"
            
            sleep = data["data"][0]
            
            return f"""😴 Sleep Data - {date}

Sleep Score: {sleep.get('score', 'N/A')}
Sleep Efficiency: {sleep.get('efficiency', 'N/A')}%
Total Sleep: {sleep.get('total', 'N/A')} seconds
REM Sleep: {sleep.get('rem', 'N/A')} seconds
Deep Sleep: {sleep.get('deep', 'N/A')} seconds
Light Sleep: {sleep.get('light', 'N/A')} seconds
Bedtime: {sleep.get('bedtime_start', 'N/A')} - {sleep.get('bedtime_end', 'N/A')}
Sleep Latency: {sleep.get('latency', 'N/A')} seconds
Time in Bed: {sleep.get('time_in_bed', 'N/A')} seconds"""
            
        except Exception as e:
            return f"❌ Error fetching sleep data: {str(e)}"

    return server
