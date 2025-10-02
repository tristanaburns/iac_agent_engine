#!/bin/bash

# Python Files Cleanup Script (Bash)
# Removes non-essential Python files and cache while preserving important scripts

echo "🧹 Python Files Cleanup Script"
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

# Run the Python cleanup script
echo "🔍 Starting Python files cleanup..."
echo ""
$PYTHON_CMD cleanup-python-files.py

echo ""
echo "✅ Python cleanup complete!"
echo "📁 Check the output above for details on what was cleaned up"