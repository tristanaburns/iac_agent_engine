#!/usr/bin/env python3
"""
Session Setup and Cleanup Script
Runs all .claude directory maintenance scripts in sequence
Perfect for start/end of session to prepare and clean up the environment
"""

import platform
import subprocess
import sys
from pathlib import Path


def detect_system():
    """Detect the operating system"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system in ["linux", "darwin"]:
        return "unix"
    else:
        return "unknown"


def run_python_script(script_name):
    """Run a Python script in the .claude directory"""
    script_dir = Path(__file__).parent.resolve()
    script_path = script_dir / script_name

    if not script_path.exists():
        print(f"   Script not found: {script_name}")
        return False

    print(f"   Running: {script_name}")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=script_dir,
        )
        if result.returncode == 0:
            print(f"   Success: {script_name}")
            # Show key output lines
            output_lines = result.stdout.strip().split("\n")
            for line in output_lines[-3:]:  # Show last 3 lines
                if line.strip():
                    print(f"     {line}")
        else:
            print(f"   Error in {script_name}:")
            print(f"     {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"   Failed to run {script_name}: {e}")
        return False


def run_shell_script(script_name):
    """Run a shell script (.sh or .bat) in the .claude directory"""
    script_dir = Path(__file__).parent.resolve()
    system = detect_system()

    if system == "windows":
        script_path = script_dir / f"{script_name}.bat"
        cmd = [str(script_path)]
    else:
        script_path = script_dir / f"{script_name}.sh"
        cmd = ["bash", str(script_path)]

    if not script_path.exists():
        print(f"   Script not found: {script_path.name}")
        return False

    print(f"   Running: {script_path.name}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=script_dir)
        if result.returncode == 0:
            print(f"   Success: {script_path.name}")
            # Show key output lines
            output_lines = result.stdout.strip().split("\n")
            for line in output_lines[-3:]:  # Show last 3 lines
                if line.strip() and not line.startswith("pause"):
                    print(f"     {line}")
        else:
            print(f"   Error in {script_path.name}:")
            error_lines = result.stderr.strip().split("\n")
            for line in error_lines[:3]:  # Show first 3 error lines
                if line.strip():
                    print(f"     {line}")
        return result.returncode == 0
    except Exception as e:
        print(f"   Failed to run {script_path.name}: {e}")
        return False


def main():
    """Main session setup function"""
    print("Claude Code Session Setup & Cleanup")
    print("=" * 50)

    system = detect_system()
    print(f"System: {system}")

    # Check if we're in a .claude directory
    current_dir = Path.cwd()
    if current_dir.name != ".claude":
        print("Warning: This script should be run from within a .claude directory")
        print(f"Current directory: {current_dir}")
        print("")

    success_count = 0
    total_scripts = 0

    print("\n1. Cleaning up Python cache files...")
    print("-" * 30)
    total_scripts += 1
    if run_python_script("cleanup-python-files.py"):
        success_count += 1

    print("\n2. Resetting MCP servers...")
    print("-" * 30)
    total_scripts += 1
    if run_shell_script("reset-mcp-servers"):
        success_count += 1

    print("\n3. Updating Claude Code documentation...")
    print("-" * 30)
    total_scripts += 1
    if run_python_script("fetch-claude-docs.py"):
        success_count += 1

    print("\n" + "=" * 50)
    print(f"Session Setup Complete: {success_count}/{total_scripts} scripts succeeded")

    if success_count == total_scripts:
        print("All operations completed successfully!")
        print("\nYour .claude directory is now ready:")
        print("- Python cache files cleaned")
        print("- MCP servers reset and configured")
        print("- Claude Code documentation updated")
    else:
        print("Some operations failed. Check the output above for details.")
        print("You may need to run individual scripts manually.")

    print("\nRecommended next step:")
    print("  claude doctor")


if __name__ == "__main__":
    main()
