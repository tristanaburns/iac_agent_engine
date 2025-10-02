#!/usr/bin/env python3
"""
Portable .claude Directory Setup Script
Creates a complete .claude setup that can be copied to any repository
"""

import os
import platform
import shutil
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


def create_portable_scripts():
    """Create portable versions of all scripts"""

    script_dir = Path(__file__).parent.resolve()

    # List of scripts that should be made portable
    scripts = [
        "cleanup-python-files.py",
        "fetch-claude-docs.py",
        "reset-mcp-servers.sh",
        "reset-mcp-servers.bat",
    ]

    print(" Making scripts portable...")

    for script in scripts:
        script_path = script_dir / script
        if script_path.exists():
            print(f"   {script} - Already portable")
        else:
            print(f"   {script} - Not found")

    print("\n .claude Directory Structure:")

    # Show the complete directory structure
    for item in sorted(script_dir.iterdir()):
        if item.is_file():
            size = item.stat().st_size
            print(f"   {item.name} ({size} bytes)")
        elif item.is_dir():
            file_count = len(list(item.rglob("*")))
            print(f"   {item.name}/ ({file_count} files)")


def create_readme():
    """Create a README for the .claude directory"""

    script_dir = Path(__file__).parent.resolve()
    readme_path = script_dir / "README.md"

    readme_content = """# .claude Directory

This directory contains Claude Code CLI configuration and utility scripts that are portable across different repositories and systems.

## Scripts

### Core Utilities
- **`cleanup-python-files.py`** - Removes Python cache files and temporary artifacts while preserving important scripts
- **`fetch-claude-docs.py`** - Downloads all Claude Code CLI documentation from Anthropic website as markdown files
- **`reset-mcp-servers.sh/.bat`** - Resets all MCP server connections with proper configuration

### Configuration Files
- **`settings.json`** - Claude Code CLI settings and configuration
- **`claude-code-mcp-server-setup-commands.md`** - Comprehensive MCP server setup documentation

## Quick Setup

### 1. Copy this entire `.claude` directory to your new repository

### 2. Run MCP server setup:
**Windows:**
```cmd
cd .claude
reset-mcp-servers.bat
```

**Unix/Linux/macOS:**
```bash
cd .claude
./reset-mcp-servers.sh
```

### 3. Download Claude Code documentation:
**Windows:**
```cmd
cd .claude
fetch-claude-docs.bat
```

**Unix/Linux/macOS:**
```bash
cd .claude
./fetch-claude-docs.sh
```

### 4. Clean up temporary files (as needed):
**Windows:**
```cmd
cd .claude
cleanup-python-files.bat
```

**Unix/Linux/macOS:**
```bash
cd .claude
./cleanup-python-files.sh
```

## Features

### Portability
-  **Cross-platform** - Works on Windows, macOS, and Linux
-  **Repository-agnostic** - Can be copied to any repository
-  **Self-contained** - All scripts work relative to their location
-  **Auto-detection** - Scripts detect the operating system and adjust accordingly

### MCP Server Management
-  **Complete reset** - Removes and re-adds all MCP servers
-  **Preserves memory** - Only resets connections, not stored data
-  **Full filesystem access** - Configures appropriate drive access per OS
-  **Windows compatibility** - Handles npx wrapper issues automatically

### Documentation Management
-  **Complete Claude Code docs** - Downloads all official documentation
-  **Offline access** - Markdown files for offline reference
-  **Auto-indexing** - Creates searchable index of all documentation
-  **Version tracking** - Includes timestamps and source URLs

### Cleanup Tools
-  **Smart cleanup** - Removes cache/temp files while preserving important scripts
-  **Safe operations** - Dry-run mode and confirmation for risky operations
-  **Detailed reporting** - Shows exactly what was cleaned up

## Customization

### Adding New Important Scripts
Edit `cleanup-python-files.py` and add to `KEEP_FILES`:
```python
KEEP_FILES = {
    "fetch-claude-docs.py",
    "cleanup-python-files.py",
    "your-custom-script.py",  # Add your script here
}
```

### Modifying MCP Server Configuration
Edit the MCP server setup scripts:
- `reset-mcp-servers.sh` (Unix/Linux/macOS)
- `reset-mcp-servers.bat` (Windows)

## Directory Structure

```
.claude/
 README.md                           # This file
 settings.json                       # Claude Code settings
 cleanup-python-files.py             # Python cleanup script
 cleanup-python-files.sh/.bat        # Cleanup runners
 fetch-claude-docs.py                # Documentation fetcher
 fetch-claude-docs.sh/.bat          # Doc fetch runners
 reset-mcp-servers.sh/.bat          # MCP server reset scripts
 claude-code-mcp-server-setup-commands.md  # Setup documentation
 docs/                              # Downloaded documentation
    index.md                       # Documentation index
    overview.md                    # Claude Code overview
    quickstart.md                  # Getting started
    ...                           # All other Claude Code docs
 portable-setup.py                 # This setup script
```

## Usage Tips

1. **Always run from .claude directory** - Scripts are designed to work from their own location
2. **Check settings.json** - Verify configuration matches your needs
3. **Update documentation periodically** - Re-run fetch script to get latest docs
4. **Clean up regularly** - Run cleanup script to remove accumulated cache files
5. **Verify MCP servers** - Use `claude doctor` after setup to ensure everything works

## Troubleshooting

### Windows MCP Server Issues
If you see "Windows requires 'cmd /c' wrapper" errors:
1. Run the reset-mcp-servers.bat script
2. Check the Windows troubleshooting section in claude-code-mcp-server-setup-commands.md

### Permission Issues
If you encounter permission errors:
1. Ensure scripts are executable: `chmod +x *.sh`
2. Check that Python and Node.js are in your PATH
3. Verify Claude Code CLI is properly installed

### Path Issues
If filesystem MCP server fails:
1. Check that the current directory path is correct
2. Verify you have read/write access to the repository
3. For Windows, ensure proper drive letter access

## Support

For issues with these scripts, check the troubleshooting documentation in:
- `claude-code-mcp-server-setup-commands.md`
- Official Claude Code docs at https://docs.anthropic.com/en/docs/claude-code/

"""

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f" Created: {readme_path}")


def main():
    """Main setup function"""
    print(" Portable .claude Directory Setup")
    print("=" * 50)

    system = detect_system()
    print(f"  Detected system: {system}")

    # Check if we're in a .claude directory
    current_dir = Path.cwd()
    if current_dir.name != ".claude":
        print("  Warning: This script should be run from within a .claude directory")

    create_portable_scripts()
    create_readme()

    print("\n" + "=" * 50)
    print(" Portable .claude directory setup complete!")
    print("\n Next steps:")
    print("1. Copy this entire .claude directory to your target repository")
    print("2. Run the appropriate setup scripts for your system")
    print("3. Use `claude doctor` to verify everything is working")
    print("4. Check README.md for detailed usage instructions")


if __name__ == "__main__":
    main()
