# Oura Ring MCP Server

An MCP (Model Context Protocol) server that provides access to Oura Ring sleep data. This server implements OAuth2 authentication with the Oura API and provides tools to fetch sleep scores and detailed sleep metrics.

## Features

- **One-Time Setup**: Simple authentication setup that saves your token for future use
- **Automatic Authentication**: No need to manually handle OAuth2 flows - just use the sleep tools directly
- **Sleep Score Data**: Get sleep scores from last night or past week
- **Detailed Sleep Metrics**: Access to comprehensive sleep data including REM, deep, and light sleep durations
- **Easy Deployment**: Ready for deployment on Smithery with proper configuration

## Local Server Deployment Setup

### 1. Oura API Credentials

1. Go to [Oura Developer Console](https://cloud.ouraring.com/oauth/applications)
2. Create a new application
3. Note down your `client_id` and `client_secret`
4. Set up a redirect URI (e.g., `http://localhost:8080/callback` for local development)

### 2. Environment Configuration

Copy the example environment file and fill in your credentials:

```bash
cp env.example .env
```

Edit `.env` with your Oura API credentials:

```env
OURA_CLIENT_ID=your_client_id_here
OURA_CLIENT_SECRET=your_client_secret_here
OURA_REDIRECT_URI=http://localhost:8080/callback
```

### 3. Installation

Install dependencies:

```bash
pip install -e .
```

## Usage

### Running the Server

```bash
python server.py
```

### Available Tools

The MCP server provides the following tools:

1. **`oura_setup_auth`**: One-time authentication setup with your Oura API access token
2. **`oura_last_night_sleep`**: Get sleep score and detailed data from last night
3. **`oura_week_sleep`**: Get sleep scores and trends from the past week

### Simple Authentication Flow

1. **One-time setup**: Use `oura_setup_auth` with your access token from [Oura Developer Console](https://cloud.ouraring.com/oauth/applications)
2. **Automatic authentication**: All future requests automatically use your saved token
3. **Just ask for data**: Use `oura_last_night_sleep` or `oura_week_sleep` directly - no more auth steps needed!

### Getting Your Access Token

1. Go to [Oura Developer Console](https://cloud.ouraring.com/oauth/applications)
2. Create a new application
3. Generate an access token
4. Use the token with `oura_setup_auth` - that's it!

## Deployment on Smithery

This server is configured for easy deployment on Smithery:

1. **Configuration**: The `smithery.yaml` file contains all necessary deployment settings
2. **Environment Variables**: Set `OURA_CLIENT_ID` and `OURA_CLIENT_SECRET` in your Smithery environment
3. **Docker Support**: Includes a `Dockerfile` for containerized deployment

### Deploy to Smithery

1. Set your environment variables in Smithery:
   - `OURA_CLIENT_ID`: Your Oura API client ID
   - `OURA_CLIENT_SECRET`: Your Oura API client secret (marked as secret)
   - `OURA_REDIRECT_URI`: Your application's redirect URI

2. Deploy using the Smithery CLI or dashboard

## API Reference

### Oura API Endpoints Used

- **Authorization**: `https://cloud.ouraring.com/oauth/authorize`
- **Token Exchange**: `https://api.ouraring.com/oauth/token`
- **Sleep Data**: `https://api.ouraring.com/v2/usercollection/sleep`

### Data Format

Sleep data includes:
- Sleep score (0-100)
- Sleep efficiency percentage
- Sleep durations (REM, deep, light, total)
- Bedtime and wake time
- Sleep latency
- Time in bed

## Development

### Project Structure

```
oura_mcp/
├── server.py          # Main MCP server implementation
├── pyproject.toml     # Python project configuration
├── smithery.yaml      # Smithery deployment configuration
├── Dockerfile         # Docker configuration
├── env.example        # Environment variables template
└── README.md          # This file
```

### Testing

You can test the server locally by setting an access token directly:

```python
# Use oura_set_token tool with a valid access token
```

## Security Notes

- Never commit your `.env` file or expose API credentials
- Use HTTPS for redirect URIs in production
- Access tokens are stored in memory only and not persisted
- Refresh tokens are handled automatically when needed

## License

This project is open source. Please check the Oura API terms of service for usage restrictions.
