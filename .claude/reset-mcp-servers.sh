#!/bin/bash

# Reset MCP Servers Script
# This script removes all MCP servers and re-adds them with proper configuration
# Memory contents are preserved - only the server connections are reset

echo "🔄 Resetting MCP Servers..."
echo "=========================================="

# Install MCP servers globally first
echo "📦 Installing MCP servers globally..."

# Install Node.js MCP servers via npm
echo "Installing Node.js MCP servers via npm..."
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @upstash/context7-mcp
npm install -g @playwright/mcp

# Install Python MCP servers via pip
echo "Installing Python MCP servers via pip..."
pip install mcp-server-fetch
pip install mcp-server-git
pip install extended-memory-mcp

# Install uvx tool for mcp-server-time
echo "Installing uvx and mcp-server-time..."
pip install uv
uvx --install-only mcp-server-time

echo "✅ All MCP servers installed globally"
echo ""

# Remove all MCP servers (but preserve memory contents)
echo "📤 Removing existing MCP servers..."

claude mcp remove memory
claude mcp remove sequential-thinking
claude mcp remove upstash-context7
claude mcp remove playwright
claude mcp remove filesystem
claude mcp remove fetch
claude mcp remove time
claude mcp remove grep
claude mcp remove git
claude mcp remove extended-memory

echo "✅ All MCP servers removed"
echo ""

# Re-add all MCP servers with proper configuration
echo "📥 Re-adding MCP servers..."

# Core servers
echo "Adding core MCP servers..."
claude mcp add memory "npx" "@modelcontextprotocol/server-memory"
claude mcp add sequential-thinking "npx" "@modelcontextprotocol/server-sequential-thinking"

# Filesystem with portable access - works on any system
# Detects current working directory and adds appropriate drive access
CURRENT_DIR=$(pwd)
if [[ "$CURRENT_DIR" =~ ^/[c-z]/ ]] || [[ "$CURRENT_DIR" =~ ^[A-Z]: ]]; then
    # Windows/WSL detected - add drive access
    claude mcp add filesystem "npx" "@modelcontextprotocol/server-filesystem" "C:\" "D:\" "E:\" "F:\" "/"
else
    # Unix/Linux detected - add root access
    claude mcp add filesystem "npx" "@modelcontextprotocol/server-filesystem" "/"
fi

# Utility servers
echo "Adding utility MCP servers..."
claude mcp add fetch "python -m" "mcp_server_fetch"
claude mcp add time "uvx" "mcp-server-time"
claude mcp add grep "mcp-remote" "https://mcp.grep.app"
claude mcp add git "python -m" "mcp_server_git"

# Research and documentation servers
echo "Adding research MCP servers..."
claude mcp add upstash-context7 "npx" "@upstash/context7-mcp"

# Advanced servers
echo "Adding advanced MCP servers..."
claude mcp add playwright "npx" "@playwright/mcp"
claude mcp add extended-memory "python -m" "extended_memory_mcp.server"

echo ""
echo "✅ All MCP servers re-added successfully!"
echo ""

# Verify configuration
echo "🔍 Verifying MCP server configuration..."
claude mcp list

echo ""
echo "🎉 MCP Server reset complete!"
echo "📝 All server connections have been reset while preserving memory contents"
echo "🔧 Run 'claude doctor' to verify all servers are working correctly"