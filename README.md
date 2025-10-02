# Simple Oura Ring OAuth2 MCP Server

Minimal MCP server for Oura Ring OAuth2 authentication.

## Setup

1. Install dependencies:
```bash
pip install mcp httpx
```

2. Set environment variables:
```bash
export OURA_CLIENT_ID="your_client_id"
export OURA_CLIENT_SECRET="your_client_secret"
export OURA_REDIRECT_URI="http://localhost:8080/callback"
```

3. Run server:
```bash
python server.py
```

## MCP Tools

- `oura_get_auth_url` - Get OAuth2 authorization URL
- `oura_exchange_code` - Exchange code for access token

## Usage

1. Call `oura_get_auth_url` to get authorization URL
2. Visit URL and authorize
3. Use callback code with `oura_exchange_code`
4. Get your access token

That's it!