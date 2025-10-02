@echo off
REM Python Files Cleanup Script (Windows)
REM Removes non-essential Python files and cache while preserving important scripts

echo 🧹 Python Files Cleanup Script
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Run the Python cleanup script
echo 🔍 Starting Python files cleanup...
echo.
python cleanup-python-files.py

echo.
echo ✅ Python cleanup complete!
echo 📁 Check the output above for details on what was cleaned up

pause