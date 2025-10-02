# 🚀 Oura MCP Server - Deployment Guide

## 📋 **Quick Start Options**

### **Option 1: Local Development (Claude Desktop)**
```bash
cd /home/eliu3765/AgentAuth/hw3/oura_mcp
pip install mcp httpx fastapi uvicorn
python3 test_server.py  # Test the server
```

### **Option 2: Smithery Deployment (Cloud)**
```bash
cd /home/eliu3765/AgentAuth/hw3/oura_mcp
# Deploy using Smithery CLI or dashboard
```

---

## 🖥️ **Local Development Setup**

### **1. Install Dependencies**
```bash
pip install mcp httpx fastapi uvicorn
```

### **2. Test the Server**
```bash
python3 test_server.py
```

### **3. Configure Claude Desktop**

#### **Method A: Using Claude Desktop UI**
1. Open Claude Desktop
2. Go to **Settings** → **MCP Servers**
3. Add new server:
   - **Name**: `oura-ring`
   - **Command**: `python3`
   - **Arguments**: `["/home/eliu3765/AgentAuth/hw3/oura_mcp/server.py"]`
   - **Working Directory**: `/home/eliu3765/AgentAuth/hw3/oura_mcp`

#### **Method B: Manual Config File**
Add to your Claude Desktop config file:
```json
{
  "mcpServers": {
    "oura-ring": {
      "command": "python3",
      "args": ["/home/eliu3765/AgentAuth/hw3/oura_mcp/server.py"],
      "env": {
        "PYTHONPATH": "/home/eliu3765/AgentAuth/hw3/oura_mcp"
      }
    }
  }
}
```

### **4. Test in Claude Desktop**
Ask Claude: *"What MCP tools are available?"*
You should see:
- `oura_setup_auth`
- `oura_last_night_sleep`
- `oura_week_sleep`

---

## ☁️ **Smithery Deployment**

### **1. Fixed Configuration Issues**
✅ **Updated `smithery.yaml`** with correct schema:
- Changed `runtime: python` to `runtime: container`
- Fixed `environmentVariables` format
- Added proper `startCommand` structure
- Included health check configuration

### **2. Environment Variables**
Set these in Smithery:
- `OURA_CLIENT_ID` (required)
- `OURA_CLIENT_SECRET` (required, secret)
- `OURA_REDIRECT_URI` (optional, defaults to localhost)

### **3. Health Checks**
The server now includes:
- HTTP health endpoint at `/health`
- Docker health check configuration
- Proper FastAPI integration

### **4. Deployment Steps**
1. **Push to Git** (if using Git-based deployment)
2. **Set environment variables** in Smithery dashboard
3. **Deploy** using Smithery CLI or dashboard
4. **Monitor** health checks and logs

---

## 🔧 **Configuration Files**

### **smithery.yaml** (Fixed)
```yaml
name: oura-mcp
description: MCP server for Oura Ring sleep data
version: 0.1.0

runtime: container

startCommand:
  command: "python"
  args: ["server.py"]

environmentVariables:
  OURA_CLIENT_ID:
    description: "Oura API client ID"
    required: true
    secret: false
  OURA_CLIENT_SECRET:
    description: "Oura API client secret"
    required: true
    secret: true

healthCheck:
  enabled: true
  path: "/health"
  interval: 30
```

### **Dockerfile** (Updated)
- Added FastAPI and uvicorn for health checks
- Included curl for health check commands
- Set proper environment variables

---

## 🧪 **Testing**

### **Local Testing**
```bash
# Test server functionality
python3 test_server.py

# Test MCP protocol
python3 test_mcp_protocol.py

# Test health endpoint
RUN_HTTP_SERVER=true python3 server.py
# Then visit: http://localhost:8080/health
```

### **Smithery Testing**
1. Check deployment logs
2. Verify health checks pass
3. Test environment variables are loaded
4. Confirm MCP tools are available

---

## 🔐 **Authentication Setup**

### **Get Oura API Token**
1. Visit [Oura Developer Console](https://cloud.ouraring.com/oauth/applications)
2. Create new application
3. Generate access token
4. Copy the token

### **Set Up in Claude**
Ask Claude: *"Set up my Oura Ring authentication"*
Provide your access token when prompted.

---

## 📊 **Usage Examples**

Once set up, ask Claude:
- *"What was my sleep score last night?"*
- *"Show me my sleep data from the past week"*
- *"How has my sleep been trending?"*
- *"What's my average sleep efficiency?"*

---

## 🛠️ **Troubleshooting**

### **Smithery Deployment Issues**
- ✅ **Fixed**: Invalid runtime configuration
- ✅ **Fixed**: Missing startCommand
- ✅ **Fixed**: Incorrect environment variables format

### **Local Development Issues**
- Check Python dependencies are installed
- Verify server path in Claude Desktop config
- Restart Claude Desktop after config changes

### **Authentication Issues**
- Verify Oura API token is valid
- Check token file was created: `~/.oura_token`
- Try re-authenticating with fresh token

---

## 🎉 **Success!**

Your Oura MCP server is now ready for both local development and cloud deployment!
