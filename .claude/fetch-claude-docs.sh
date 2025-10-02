#!/bin/bash

# Claude Code Documentation Fetcher (Bash)
# Downloads all Claude Code CLI documentation from Anthropic website

echo "🚀 Claude Code Documentation Fetcher"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed or not in PATH"
        echo "Please install Python and try again"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

echo "✅ Using Python: $PYTHON_CMD"

# Install required Python packages
echo "📦 Installing required Python packages..."
$PYTHON_CMD -m pip install requests beautifulsoup4 markdownify pathlib

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python packages"
    exit 1
fi

# Create docs directory
if [ ! -d ".claude/docs" ]; then
    mkdir -p ".claude/docs"
    echo "📁 Created .claude/docs directory"
fi

# Run the documentation fetcher
echo "🌐 Starting documentation download..."
echo ""
$PYTHON_CMD fetch-claude-docs.py

echo ""
echo "✅ Documentation fetch complete!"
echo "📁 Check .claude/docs/ for downloaded files"
echo "📖 Open .claude/docs/index.md for an overview"