@echo off
REM Claude Code Documentation Fetcher (Windows)
REM Downloads all Claude Code CLI documentation from Anthropic website

echo 🚀 Claude Code Documentation Fetcher
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Install required Python packages
echo 📦 Installing required Python packages...
pip install requests beautifulsoup4 markdownify pathlib

if errorlevel 1 (
    echo ❌ Failed to install Python packages
    pause
    exit /b 1
)

REM Create docs directory
if not exist ".claude\docs" (
    mkdir ".claude\docs"
    echo 📁 Created .claude\docs directory
)

REM Run the documentation fetcher
echo 🌐 Starting documentation download...
echo.
python fetch-claude-docs.py

echo.
echo ✅ Documentation fetch complete!
echo 📁 Check .claude\docs\ for downloaded files
echo 📖 Open .claude\docs\index.md for an overview

pause