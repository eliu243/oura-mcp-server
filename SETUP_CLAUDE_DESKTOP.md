# 🖥️ Setting up Oura MCP Server with Claude Desktop

## 📋 **Step-by-Step Setup**

### **1. Install Dependencies**
```bash
cd /home/eliu3765/AgentAuth/hw3/oura_mcp
pip install mcp httpx
```

### **2. Test the Server Locally**
```bash
# Test that the server works
python3 test_server.py

# Or run the server directly (will show MCP protocol messages)
python3 server.py
```

### **3. Configure Claude Desktop**

#### **Option A: Using Claude Desktop Settings UI**
1. Open **Claude Desktop**
2. Go to **Settings** (gear icon)
3. Click **"Add Server"** or **"MCP Servers"**
4. Add a new server with these settings:
   - **Name**: `oura-ring`
   - **Command**: `python3`
   - **Arguments**: `["/home/eliu3765/AgentAuth/hw3/oura_mcp/server.py"]`
   - **Working Directory**: `/home/eliu3765/AgentAuth/hw3/oura_mcp`

#### **Option B: Manual Config File (Advanced)**
1. Find your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add this configuration:
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

### **4. Restart Claude Desktop**
After adding the configuration, restart Claude Desktop completely.

### **5. Test in Claude Desktop**
1. Open Claude Desktop
2. Start a new conversation
3. Ask: *"What MCP tools are available?"*
4. You should see the Oura tools listed:
   - `oura_setup_auth`
   - `oura_last_night_sleep`
   - `oura_week_sleep`

## 🔐 **First-Time Authentication Setup**

### **Get Your Oura API Token**
1. Go to [Oura Developer Console](https://cloud.ouraring.com/oauth/applications)
2. Create a new application
3. Generate an access token
4. Copy the token

### **Set Up Authentication in Claude**
1. In Claude Desktop, ask: *"Set up my Oura Ring authentication"*
2. Provide your access token when prompted
3. Claude will use the `oura_setup_auth` tool to save your token

## 🎯 **Using Your Sleep Data**

Once authenticated, you can ask:
- *"What was my sleep score last night?"*
- *"Show me my sleep data from the past week"*
- *"How has my sleep been trending?"*

## 🛠️ **Troubleshooting**

### **Server Not Starting**
```bash
# Check if Python can find the MCP package
python3 -c "import mcp; print('MCP installed successfully')"

# Test server manually
cd /home/eliu3765/AgentAuth/hw3/oura_mcp
python3 server.py
```

### **Claude Can't Find Tools**
1. Check Claude Desktop logs for errors
2. Ensure the server path is correct
3. Restart Claude Desktop after config changes

### **Authentication Issues**
1. Verify your Oura API token is valid
2. Check that the token file was created: `~/.oura_token`
3. Try setting up authentication again

## 📁 **File Locations**
- **Server**: `/home/eliu3765/AgentAuth/hw3/oura_mcp/server.py`
- **Token Storage**: `~/.oura_token`
- **Config Template**: `/home/eliu3765/AgentAuth/hw3/oura_mcp/claude_desktop_config.json`

## 🎉 **You're Ready!**
Once set up, you can seamlessly ask Claude about your Oura Ring sleep data without any manual authentication steps!
