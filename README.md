# Oura Ring OAuth2 MCP Server

Complete Oura Ring integration with OAuth2 authentication and sleep data access using FastMCP and Smithery.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Test locally:
```bash
uv run playground
```

## MCP Tools

### OAuth2 Authentication
- `get_auth_url` - Get OAuth2 authorization URL
- `exchange_code` - Exchange code for access token (auto-stores token)
- `parse_redirect_url` - Parse redirect URL and auto-extract token (smoother UX)
- `set_access_token` - Manually set access token (backup method)

### Sleep Data
- `get_sleep_last_night` - Get sleep data from last night
- `get_sleep_last_week` - Get sleep data from past week with average score
- `get_sleep_by_date` - Get sleep data for specific date (YYYY-MM-DD)

## Usage

### 1. OAuth2 Authentication
1. Set session configuration with your Oura API credentials (`client_id`, `client_secret`, `redirect_uri`)
2. Call `get_auth_url` to get authorization URL
3. Visit URL and authorize
4. Copy the entire redirect URL
5. Use `parse_redirect_url` with the full URL (auto-extracts and stores token)

### 2. Access Sleep Data
Once authenticated, use any sleep data tool:
- "What was my sleep score last night?"
- "Show me my sleep data from the past week"
- "Get my sleep data for 2024-10-01"

## Session Configuration

Set these in Smithery dashboard:
- `client_id` - Oura API client ID (required)
- `client_secret` - Oura API client secret (required)
- `redirect_uri` - OAuth2 redirect URI (default: http://localhost:8080/callback)
- `access_token` - Auto-populated after OAuth2 authentication

## Deploy

Push to GitHub and deploy via Smithery dashboard.
