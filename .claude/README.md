# .claude Directory

This directory contains Claude Code CLI configuration and utility scripts that are portable across different repositories and systems.

## Scripts

### Core Utilities
- **`session-setup.py/.sh/.bat`** - Master script that runs all setup/cleanup operations in sequence (RECOMMENDED)
- **`cleanup-python-files.py`** - Removes Python cache files and temporary artifacts while preserving important scripts
- **`fetch-claude-docs.py`** - Downloads all Claude Code CLI documentation from Anthropic website as markdown files
- **`reset-mcp-servers.sh/.bat`** - Resets all MCP server connections with proper configuration

### Configuration Files
- **`settings.json`** - Claude Code CLI settings and configuration
- **`claude-code-mcp-server-setup-commands.md`** - Comprehensive MCP server setup documentation

## Quick Setup

### 1. Copy this entire `.claude` directory to your new repository

### 2. Run complete session setup (RECOMMENDED):
**Windows:**
```cmd
cd .claude
session-setup.bat
```

**Unix/Linux/macOS:**
```bash
cd .claude
./session-setup.sh
```

This master script automatically runs all setup operations:
- Cleans Python cache files
- Resets MCP servers
- Updates Claude Code documentation

### Individual Script Usage (if needed):

**Reset MCP servers only:**
```bash
# Windows: reset-mcp-servers.bat
# Unix: ./reset-mcp-servers.sh
```

**Update documentation only:**
```bash
# Windows: fetch-claude-docs.bat
# Unix: ./fetch-claude-docs.sh
```

**Clean cache files only:**
```bash
# Windows: cleanup-python-files.bat
# Unix: ./cleanup-python-files.sh
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

1. **Use session-setup script** - Run `session-setup.bat/sh` at start/end of sessions for complete maintenance
2. **Always run from .claude directory** - Scripts are designed to work from their own location
3. **Check settings.json** - Verify configuration matches your needs
4. **Verify MCP servers** - Use `claude doctor` after setup to ensure everything works
5. **Portable design** - Copy entire .claude directory to any repository and run setup

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
