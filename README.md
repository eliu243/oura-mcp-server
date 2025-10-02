# Oura Ring OAuth2 MCP Server

Simple Oura Ring OAuth2 authentication using FastMCP and Smithery.

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

- `get_auth_url` - Get OAuth2 authorization URL
- `exchange_code` - Exchange code for access token

## Usage

1. Set session configuration with your Oura API credentials
2. Call `get_auth_url` to get authorization URL
3. Visit URL and authorize
4. Use callback code with `exchange_code`
5. Get your access token

## Deploy

Push to GitHub and deploy via Smithery dashboard.
