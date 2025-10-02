#!/bin/bash
# Setup script for Oura MCP Server

echo "🚀 Setting up Oura MCP Server..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install mcp httpx

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your Oura API credentials!"
    echo "   Get them from: https://cloud.ouraring.com/oauth/applications"
else
    echo "✅ .env file already exists"
fi

# Make server executable
chmod +x server.py

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Oura API credentials"
echo "2. Run: python3 server.py"
echo "3. Or test with: python3 test_server.py"
