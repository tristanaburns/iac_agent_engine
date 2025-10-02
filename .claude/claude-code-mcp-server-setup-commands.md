# MCP Server Setup Commands

Run these commands in your project directory to add all MCP servers to your Claude Code configuration.

## Quick Start

1. **Install global packages** (see sections below)
2. **Add servers to Claude Code** (see individual sections)
3. **Configure advanced servers** (see Manual Configuration section)
4. **Create required directories** (see Additional Setup Steps)
5. **Verify installation** (see Verification section)

###########################################################################################################

## MCP Server installation (global)

Install these MCP servers globally on your system before adding them to Claude Code:

### NPM Global Installation (Node.js packages)

```bash
# Core MCP Servers
mkdir -p ./mcp/server-memory
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-filesystem

# Utility Servers
npm install -g @upstash/context7-mcp
npm install -g mcp-remote

# Advanced Servers
npm install -g @playwright/mcp

# Frontend Development Servers
npm install -g @jpisnice/shadcn-ui-mcp-server
npm install -g @chakra-ui/react-mcp
npm install -g @magicuidesign/mcp
npm install -g heroui-mcp
npm install -g lucide-icons-mcp
npm install -g vite-plugin-mcp
# Note: @vercel/mcp-adapter and mcp-react are not standalone MCP servers
```

###########################################################################################################

### UV Global Installation (Python packages)

```bash
# Core MCP Servers
uv pip install mcp-server-fetch

# Utility Servers
uv pip install mcp-server-time

# grep Server
uv pip install mcp-server-git

# Advanced Servers
# uv pip install extended-memory-mcp
# uv pip install zen-mcp-server
```

### Alternative: Using pip directly

```bash
# Core MCP Servers
pip install mcp-server-fetch

# git server tools
pip install mcp-server-git

# Utility Servers
pip install mcp-server-time

# Advanced Servers
# pip install extended-memory-mcp
# pip install zen-mcp-server
```

### Note about Grep Server

The grep server uses a remote URL and doesn't require local installation:

- URL: `https://mcp.grep.app`

###########################################################################################################

## Core MCP Servers

```bash
# Basic memory server (replaced by Neo4j Graph Memory)
claude mcp add memory "npx" "@modelcontextprotocol/server-memory"

# Sequential thinking for enhanced reasoning
claude mcp add sequential-thinking "npx" "@modelcontextprotocol/server-sequential-thinking"

# Filesystem access
# claude mcp add filesystem "npx" "@modelcontextprotocol/server-filesystem" "c:\\" "/c/" "d:\\" "/d/" "/"
claude mcp add filesystem "npx" "@modelcontextprotocol/server-filesystem" "c:\\" "/c/" "/"

# Web fetch capabilities
claude mcp add fetch "python -m" "mcp_server_fetch"
```

## Additional Utility Servers

```bash
# Time server
claude mcp add time "python -m" "mcp_server_time"
# claude mcp add time "uvx" "mcp-server-time"

# Grep server for remote searching
claude mcp add grep "mcp-remote" "https://mcp.grep.app"

# git server tools
claude mcp add git "python -m" "mcp_server_git"

# Upstash context management
claude mcp add upstash-context7 "npx" "@upstash/context7-mcp"

# Playwright browser automation
claude mcp add playwright "npx" "@playwright/mcp"

# Neo4j Graph Memory Server (Local Kubernetes)
# Option 1: Direct LoadBalancer (Recommended)
claude mcp add neo4j-memory -t http http://localhost:9999/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"

# Option 2: Direct NodePort
claude mcp add neo4j-memory -t http http://localhost:31999/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"

# Option 3: Traefik Ingress (Requires hosts file setup)
claude mcp add neo4j-memory -t http http://mcp-neo4j-memory.local/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"
```

###########################################################################################################

## Advanced MCP Servers

```bash
# Playwright browser automation
claude mcp add playwright "npx" "@playwright/mcp"
# Note: After adding, manually edit .claude.json to add "-y" to args and:
# "env": {
#   "PW_MCP_HEADLESS": "1",
#   "PW_MCP_CAPS": ""
# }

# Extended memory with SQLite backend
claude mcp add extended-memory "python -m" extended_memory_mcp.server"
# Note: After adding, manually edit .claude.json to add:
# "args": ["-m", "extended_memory_mcp.server"],
# "env": {
#   "LOG_LEVEL": "INFO",
#   "STORAGE_CONNECTION_STRING": "sqlite:///./extended-memory/extended-memory.db"
# }

# Zen multi-model AI collaboration
claude mcp add zen "python"
# Note: After adding, manually edit .claude.json to add:
# "args": ["-m", "zen_mcp_server"],
# "env": {
#   "DEFAULT_MODEL": "auto",
#   "GEMINI_API_KEY": "",
#   "OPENAI_API_KEY": "",
#   "DIAL_API_KEY": ""
# }

```

###########################################################################################################

## Frontend Development MCP Servers

```bash
# UI Component Libraries
claude mcp add shadcn-ui "npx" "@jpisnice/shadcn-ui-mcp-server"
claude mcp add chakra-ui "npx" "@chakra-ui/react-mcp"
claude mcp add magicui "npx" "@magicuidesign/mcp"
claude mcp add heroui "npx" "heroui-mcp"

# Icon Libraries
claude mcp add lucide-icons "npx" "lucide-icons-mcp"

# Build Tools & Frameworks
claude mcp add vite-plugin "npx" "vite-plugin-mcp"
# Note: @vercel/mcp-adapter and mcp-react are not standalone MCP servers
```

###########################################################################################################

## All-in-One Setup Script

To add all servers at once, you can run this bash script:

```bash
#!/bin/bash

# Core servers
claude mcp add memory "npx" "@modelcontextprotocol/server-memory"  # Replaced by Neo4j
claude mcp add sequential-thinking "npx" "@modelcontextprotocol/server-sequential-thinking"
claude mcp add filesystem "npx" "@modelcontextprotocol/server-filesystem" "c:\\" "/c/" "d:\\" "/d/" "/"
claude mcp add fetch "python -m" "mcp_server_fetch"

# Utility servers
claude mcp add time "python -m" "mcp_server_time"
claude mcp add grep "mcp-remote" "https://mcp.grep.app"
claude mcp add upstash-context7 "npx" "@upstash/context7-mcp"

# Advanced servers (require manual config)
# mkdir extended-memory
# claude mcp add extended-memory "python -m" "extended_memory_mcp.server"
claude mcp add playwright "npx" "@playwright/mcp"

# Neo4j Graph Memory Server (Local Kubernetes)
# claude mcp add neo4j-memory -t http http://localhost:9999/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"
claude mcp add neo4j-memory -t http http://mcp-neo4j-memory.local/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"

# Advanced orchestration
# claude mcp add zen "python -m" "zen_mcp_server"
# Frontend servers
claude mcp add shadcn-ui "npx" "@jpisnice/shadcn-ui-mcp-server"
claude mcp add chakra-ui "npx" "@chakra-ui/react-mcp"
claude mcp add magicui "npx" "@magicuidesign/mcp"
claude mcp add heroui "npx" "heroui-mcp"
claude mcp add lucide-icons "npx" "lucide-icons-mcp"
claude mcp add vite-plugin "npx" "vite-plugin-mcp"
# Note: @vercel/mcp-adapter and mcp-react are not standalone MCP servers

echo "All MCP servers added! Remember to manually configure extended-memory, zen, and playwright in .claude.json"
```

###########################################################################################################

## Local Kubernetes MCP Neo4j Memory Setup

### Complete Setup Guide

**Step 1: Deploy to Kubernetes**

```bash
# Navigate to deployment directory
cd D:\github_development\mcp-servers\mcp-neo4j-memory\deployments\local

# Deploy the service
kubectl apply -f production-ready-deploy.yaml

# Verify deployment
kubectl get pods -n mcp-neo4j-memory
kubectl get services -n mcp-neo4j-memory
kubectl get ingress -n mcp-neo4j-memory
```

**Step 2: Setup Hosts File (For Traefik Ingress)**

```powershell
# Run PowerShell as Administrator
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "127.0.0.1    mcp-neo4j-memory.local neo4j-memory.local"

# Verify hosts file entry
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-Object -Last 5
```

**Step 3: Add to Claude Code**

```bash
# Option 1: Direct LoadBalancer (Recommended)
claude mcp add neo4j-memory -t http http://localhost:9999/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"

# Option 2: Direct NodePort
claude mcp add neo4j-memory -t http http://localhost:31999/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"

# Option 3a: Traefik Ingress via NodePort (Docker Desktop default)
# Requires hosts file entry and Traefik NodePort (typically 30000)
claude mcp add neo4j-memory -t http http://mcp-neo4j-memory.local:30000/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"

# Option 3b: Traefik Ingress via LoadBalancer (if Traefik svc is LoadBalancer)
claude mcp add neo4j-memory -t http http://mcp-neo4j-memory.local/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"
```

**Step 4: Verify Connection**

```bash
# Test MCP server endpoint
curl -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456" http://localhost:9999/mcp-neo4j-memory/

# Test Traefik via NodePort (Docker Desktop default)
curl -H "Host: mcp-neo4j-memory.local" -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456" http://localhost:30000/mcp-neo4j-memory/

# Test Traefik via LoadBalancer (if enabled)
curl -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456" http://mcp-neo4j-memory.local/mcp-neo4j-memory/

# Check Claude Code MCP servers
claude mcp list
```

**Service Configuration Details:**

- **Namespace**: `mcp-neo4j-memory`
- **MCP Server Port**: `9999` (internal)  `9999/9998` (LoadBalancer)  `31999` (NodePort)
- **Neo4j Port**: `7687` (internal ClusterIP)
- **Neo4j Browser**: `7474` (internal ClusterIP)
- **API Key**: `mcp-neo4j-secure-key-2025-1737123456`
- **Traefik Hostnames**: `mcp-neo4j-memory.local`, `neo4j-memory.local`

**Troubleshooting:**

```bash
# Check pod status
kubectl get pods -n mcp-neo4j-memory -o wide

# Check service endpoints
kubectl get endpoints -n mcp-neo4j-memory

# Check ingress status
kubectl describe ingress mcp-neo4j-ingress -n mcp-neo4j-memory

# Check Traefik logs
kubectl logs -n traefik-system deployment/traefik --tail=50

# Check Traefik service type/ports
kubectl -n traefik-system get svc traefik -o wide

# If Traefik is NodePort, test with Host header
curl -H "Host: mcp-neo4j-memory.local" -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456" http://localhost:30000/mcp-neo4j-memory/

# Optional: Switch Traefik to LoadBalancer (Docker Desktop supports this)
kubectl -n traefik-system patch svc traefik -p '{"spec":{"type":"LoadBalancer"}}'
```

###########################################################################################################

## Manual Configuration Required

After running the setup commands, you'll need to manually edit your `.claude.json` file to add the proper arguments and environment variables for these servers:

### NEO4J Memory Server

```json
"neo4j-memory": {
  "type": "stdio",
  "command": "python",
  "args": ["-m", "mcp_neo4j_memory"],
  "env": {
    "NEO4J_URL": "bolt://localhost:32687",
    "NEO4J_USERNAME": "neo4j",
    "NEO4J_PASSWORD": "SecurePassword123!",
    "NEO4J_DATABASE": "neo4j"
  }
}
```

### Fetch Server

```json
"fetch": {
  "type": "stdio",
  "command": "python",
  "args": ["-m", "mcp_server_fetch"],
  "env": {}
}
```

### Extended Memory Server

```json
"extended-memory": {
      "command": "python",
      "args": ["-m", "extended_memory_mcp.server"],
      "cwd": ".",
      "env": {
        "LOG_LEVEL": "INFO",
        "STORAGE_CONNECTION_STRING": "sqlite:///extended-memory/extended-memory.db"
      }
    }
```

### Neo4j Graph Memory Server (Local Kubernetes)

**Prerequisites:**

1. Kubernetes cluster running (Docker Desktop, minikube, or cloud)
2. Traefik ingress controller installed
3. MCP Neo4j Memory service deployed

**Installation Steps:**

# Install Traefik (local manifests)

```bash
kubectl apply -f D:\github_development\mcp-servers\mcp-neo4j-memory\deployments\local\traefik\namespace.yaml
kubectl apply -f D:\github_development\mcp-servers\mcp-neo4j-memory\deployments\local\traefik\rbac.yaml
kubectl apply -f D:\github_development\mcp-servers\mcp-neo4j-memory\deployments\local\traefik\deployment.yaml
kubectl apply -f D:\github_development\mcp-servers\mcp-neo4j-memory\deployments\local\traefik\service.yaml
# Optional: switch Traefik svc to LoadBalancer
# kubectl apply -f D:\github_development\mcp-servers\mcp-neo4j-memory\deployments\local\traefik\values-loadbalancer.yaml
```

```bash
# 1. Deploy to Kubernetes (one-time setup)
cd D:\github_development\mcp-servers\mcp-neo4j-memory\deployments\local
kubectl apply -f production-ready-deploy.yaml

# 2. Verify deployment
kubectl get pods -n mcp-neo4j-memory
kubectl get services -n mcp-neo4j-memory

# 3. Check service endpoints
kubectl get endpoints -n mcp-neo4j-memory
```

**Hosts File Setup (Required for Traefik Ingress):**

```powershell
# Run PowerShell as Administrator
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "127.0.0.1    mcp-neo4j-memory.local neo4j-memory.local"
```

**Claude Code Configuration:**

```bash
# Option 1: Direct LoadBalancer (Recommended)
claude mcp add neo4j-memory -t http http://localhost:9999/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"

# Option 2: Direct NodePort
claude mcp add neo4j-memory -t http http://localhost:31999/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"

# Option 3a: Traefik Ingress via NodePort (Docker Desktop default)
claude mcp add neo4j-memory -t http http://mcp-neo4j-memory.local:30000/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"

# Option 3b: Traefik Ingress via LoadBalancer (if Traefik svc is LoadBalancer)
claude mcp add neo4j-memory -t http http://mcp-neo4j-memory.local/mcp-neo4j-memory/ -H "Authorization: Bearer mcp-neo4j-secure-key-2025-1737123456"
```

**Manual JSON Configuration (.claude.json):**

```json
"neo4j-memory": {
  "type": "http",
  "url": "http://localhost:9999/mcp-neo4j-memory/",
  "headers": {
    "Authorization": "Bearer mcp-neo4j-secure-key-2025-1737123456"
  }
}
```

**Key Features:**

- Graph-based memory with entity relationships
- Persistent storage across sessions
- Semantic search capabilities
- Cross-project pattern discovery
- Temporal tracking and evolution
- Success metrics and learning feedback
- API key authentication
- Kubernetes-native deployment

**Service Details:**

- **MCP Server**: LoadBalancer on port 80/443/9999  NodePort 31999
- **Neo4j Database**: ClusterIP on port 7687 (internal)
- **Neo4j Browser**: ClusterIP on port 7474 (internal)
- **API Key**: `mcp-neo4j-secure-key-2025-1737123456`
- **Traefik Ingress**: `mcp-neo4j-memory.local/mcp-neo4j-memory/` and `neo4j-memory.local/`

**Access Methods:**

1. **Direct LoadBalancer**: `http://localhost:9999/mcp-neo4j-memory/`
2. **NodePort**: `http://localhost:31999/mcp-neo4j-memory/`
3. **Traefik Ingress**: `http://mcp-neo4j-memory.local/mcp-neo4j-memory/`
4. **Neo4j Browser**: Port-forward to `http://localhost:7474`

### Zen Server

```json
"zen": {
  "type": "stdio",
  "command": "python",
  "args": ["-m", "zen_mcp_server"],
  "env": {
    "DEFAULT_MODEL": "auto",
    "GEMINI_API_KEY": "your-api-key-here",
    "OPENAI_API_KEY": "your-api-key-here",
    "DIAL_API_KEY": "your-api-key-here"
  }
}
```

### Playwright Server

```json
"playwright": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@playwright/mcp"],
  "env": {
    "PW_MCP_HEADLESS": "1",
    "PW_MCP_CAPS": ""
  }
}
```

###########################################################################################################

## Verification

After installing and configuring all MCP servers, you can verify they're working:

```bash
# List all configured MCP servers
claude mcp list

# Check server health status
claude mcp health
```

###########################################################################################################

## Notes

- These commands add MCP servers to the current project only
- To use in a different project, navigate to that project directory and run the commands again
- Some servers require additional dependencies (Python, Node.js, etc.)
- API keys should be added to the environment variables where needed
- After adding servers, restart Claude Code for changes to take effect
- The grep server requires `mcp-remote` to be installed globally
- The fetch server is a Python package (`mcp-server-fetch`), not an npm package
- `@vercel/mcp-adapter` and `mcp-react` are development tools, not standalone MCP servers
- **Neo4j Graph Memory** replaces the basic memory server with advanced graph-based persistent storage
- Neo4j requires Kubernetes cluster (Docker Desktop, minikube, or cloud) to be installed and running
- Neo4j memory persists across sessions unlike the basic memory server
- Neo4j MCP server now uses HTTP transport with API key authentication
- Traefik ingress controller required for custom hostname access
- Hosts file modification required for local development with custom domains

## Development Tools (Not MCP Servers)

These packages are development tools that help integrate MCP capabilities into your projects:

### Vercel MCP Adapter

The `@vercel/mcp-adapter` (now `mcp-handler`) is used to add MCP capabilities to Next.js applications:

```bash
# Install the package
npm install -g mcp-handler
npm install mcp-handler
npm install mcp-react

# Create MCP route in your Next.js project
cd your-nextjs-project
create-mcp-route

# Or use the mcp-adapter command
mcp-adapter
```

This creates API routes in your Next.js app that can handle MCP requests.

### MCP React

The `mcp-react` package is a React library for building MCP applications:

```bash
# Install in your React project
npm install mcp-react

# Use in your React components
import { useMCP } from 'mcp-react';
```

This provides React hooks and components for integrating MCP functionality into React applications.

###########################################################################################################

### Usage Examples

**For Next.js projects:**

```bash
# Navigate to your Next.js project
cd my-nextjs-app

# Create MCP route handler
create-mcp-route

# This will create:
# - app/api/mcp/route.ts (or pages/api/mcp.ts)
# - Configuration for MCP integration
```

**For React projects:**

```javascript
// In your React component
import { useMCP } from "mcp-react";

function MyComponent() {
  const { tools, sendMessage } = useMCP();

  // Use MCP tools in your React app
  return <div>{/* Your MCP-enabled React components */}</div>;
}
```

###########################################################################################################

## Windows MCP Server Troubleshooting & Fixes

### Windows cmd /c Wrapper Issues

On Windows, MCP servers that use `npx` may fail with "Windows requires 'cmd /c' wrapper to execute npx" errors. If you encounter this issue after running `claude doctor`, use these commands to fix all affected MCP servers:

**Step 1: Remove and Re-add Core MCP Servers with Windows Wrappers**

```bash
# Remove existing servers that have Windows npx issues
claude mcp remove memory
claude mcp remove sequential-thinking
claude mcp remove upstash-context7
claude mcp remove playwright
claude mcp remove filesystem

# Re-add with proper Windows cmd /c wrappers
claude mcp add memory -- cmd /c npx -y @modelcontextprotocol/server-memory
claude mcp add sequential-thinking -- cmd /c npx -y @modelcontextprotocol/server-sequential-thinking
claude mcp add upstash-context7 -- cmd /c npx -y @upstash/context7-mcp
claude mcp add playwright -- cmd /c npx -y @playwright/mcp
# Use current directory for portability - replace with your project path as needed
claude mcp add filesystem -- cmd /c npx -y @modelcontextprotocol/server-filesystem "%CD%"
```

**Step 2: Verify Windows MCP Server Configuration**

```bash
# List all configured MCP servers to verify Windows fixes
claude mcp list

# Run doctor again to confirm all Windows issues are resolved
claude doctor
```

**Step 3: Frontend Development Servers (If Needed)**

```bash
# If you have frontend development servers, fix them too:
claude mcp remove shadcn-ui
claude mcp remove chakra-ui
claude mcp remove magicui
claude mcp remove heroui
claude mcp remove lucide-icons
claude mcp remove vite-plugin

# Re-add with Windows wrappers
claude mcp add shadcn-ui -- cmd /c npx -y @jpisnice/shadcn-ui-mcp-server
claude mcp add chakra-ui -- cmd /c npx -y @chakra-ui/react-mcp
claude mcp add magicui -- cmd /c npx -y @magicuidesign/mcp
claude mcp add heroui -- cmd /c npx -y heroui-mcp
claude mcp add lucide-icons -- cmd /c npx -y lucide-icons-mcp
claude mcp add vite-plugin -- cmd /c npx -y vite-plugin-mcp
```

### Windows-Specific MCP Server Notes

**Important Windows Considerations:**

- **Command Wrapper Required**: All `npx` commands must be wrapped with `cmd /c` on Windows
- **Path Separators**: Use Windows-style paths for filesystem server (e.g., `C:\GitHub_Development\ai-agents`)
- **Double Backslashes**: In some configurations, you may need `C:\\path\\to\\directory`
- **PowerShell vs CMD**: These commands work in both PowerShell and Command Prompt
- **WSL Alternative**: Consider using WSL2 for better Linux compatibility if needed

**Why This Happens:**

Windows cannot directly execute `npx` commands without the shell wrapper. The `cmd /c` prefix tells Windows to execute the command through the command shell, which provides proper `npx` execution context.

**Post-Fix Verification:**

After applying these fixes, your `.claude.json` configuration should show commands like:
```json
"memory": {
  "type": "stdio",
  "command": "cmd",
  "args": ["C:/", "npx", "-y", "@modelcontextprotocol/server-memory"]
}
```

This ensures all MCP servers work correctly on Windows systems without the "Windows requires 'cmd /c' wrapper" errors.

###########################################################################################################
