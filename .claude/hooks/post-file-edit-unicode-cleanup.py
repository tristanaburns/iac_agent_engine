#!/usr/bin/env python3
"""
Post-File-Edit Unicode Cleanup Hook.

===================================

Automatically runs Unicode/emoji cleanup after Claude Code file write/edit operations.
This hook triggers whenever Write, Edit, MultiEdit, or NotebookEdit tools are used,
ensuring Windows console compatibility by removing problematic Unicode characters.

Hook Type: PostToolUse
Triggers: After Write, Edit, MultiEdit, NotebookEdit tools
Action: Run Unicode cleanup on modified files
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add tools directory to Python path
tools_dir = Path(__file__).parent / "tools"
sys.path.insert(0, str(tools_dir))

try:
    from tools.unicode_manager import UnicodeManager
except ImportError:
    print(f"[ERROR] Could not import UnicodeManager from {tools_dir}")
    sys.exit(1)


def log_message(message: str, level: str = "INFO", write_to_file: bool = True) -> str:
    """Create a timestamped log message and optionally write to file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] [{level}] {message}"

    # Write to log file
    if write_to_file:
        try:
            project_dir = Path.cwd()
            log_file = (
                project_dir
                / ".claude"
                / "hooks"
                / "quality-checks"
                / "unicode-cleanup.log"
            )
            log_file.parent.mkdir(parents=True, exist_ok=True)

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(formatted_msg + "\n")
        except Exception:
            pass  # Silent fail if can't write log

    return formatted_msg


def extract_file_paths_from_tool_result(
    tool_name: str, tool_input: Dict[str, Any]
) -> List[Path]:
    """Extract file paths that were modified from tool input."""
    file_paths: List[Path] = []

    try:
        if tool_name == "Write":
            # Write tool creates/overwrites a file
            if "file_path" in tool_input:
                file_paths.append(Path(tool_input["file_path"]))

        elif tool_name == "Edit":
            # Edit tool modifies an existing file
            if "file_path" in tool_input:
                file_paths.append(Path(tool_input["file_path"]))

        elif tool_name == "MultiEdit":
            # MultiEdit modifies a single file with multiple edits
            if "file_path" in tool_input:
                file_paths.append(Path(tool_input["file_path"]))

        elif tool_name == "NotebookEdit":
            # NotebookEdit modifies a Jupyter notebook
            if "notebook_path" in tool_input:
                file_paths.append(Path(tool_input["notebook_path"]))

    except Exception as e:
        print(log_message(f"Error extracting file paths from {tool_name}: {e}", "WARN"))

    return file_paths


def should_cleanup_file(file_path: Path) -> bool:
    """Determine if file should be cleaned up."""
    # Skip backup files (inert files ending with .backup)
    if file_path.name.endswith(".backup"):
        return False

    # Skip any files in backup directories
    if "backups" in file_path.parts:
        return False

    # Only process text-based files that might contain Unicode
    text_extensions = {
        ".py",
        ".md",
        ".txt",
        ".yml",
        ".yaml",
        ".json",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
    }

    # Check file extension
    if file_path.suffix.lower() not in text_extensions:
        return False

    # Skip if file doesn't exist
    if not file_path.exists():
        return False

    # Skip very large files (>1MB)
    try:
        if file_path.stat().st_size > 1024 * 1024:
            return False
    except OSError:
        return False

    return True


def cleanup_unicode_in_files(file_paths: List[Path]) -> Dict[str, Any]:
    """Run Unicode cleanup on the specified files."""
    cleanup_stats: Dict[str, Any] = {
        "files_processed": 0,
        "files_modified": 0,
        "unicode_replaced": 0,
        "files_skipped": 0,
        "errors": [],
    }

    if not file_paths:
        return cleanup_stats

    # Initialize Unicode Manager
    unicode_manager = UnicodeManager()

    for file_path in file_paths:
        try:
            if not should_cleanup_file(file_path):
                cleanup_stats["files_skipped"] += 1
                continue

            # Process the file
            result = unicode_manager.process_file(file_path)

            if result["processed"]:
                cleanup_stats["files_processed"] += 1

                if result["modified"]:
                    cleanup_stats["files_modified"] += 1
                    cleanup_stats["unicode_replaced"] += result["unicode_replaced"]
                    replacements = result["unicode_replaced"]
                    print(
                        log_message(
                            f"Cleaned Unicode in: {file_path} ({replacements} replacements)"
                        )
                    )

            elif result["error"] and "excluded" not in result["error"]:
                cleanup_stats["errors"].append(f"{file_path}: {result['error']}")

        except Exception as e:
            cleanup_stats["errors"].append(f"{file_path}: {str(e)}")
            print(log_message(f"Error cleaning {file_path}: {e}", "ERROR"))

    return cleanup_stats


def _parse_hook_input() -> dict:
    """Parse hook input from stdin or environment variables."""
    hook_input = {}

    # Try to read from stdin (Claude Code passes hook data this way)
    if not sys.stdin.isatty():
        try:
            input_data = sys.stdin.read().strip()
            if input_data:
                hook_input = json.loads(input_data)
        except (json.JSONDecodeError, Exception):
            # If we can't parse input, check environment variables
            pass

    return hook_input


def _should_process_tool(tool_name: str) -> bool:
    """Check if the tool is a file modification tool that should be processed."""
    file_tools = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
    return tool_name in file_tools


def _report_cleanup_results(cleanup_stats: dict) -> None:
    """Report the results of Unicode cleanup operation."""
    if cleanup_stats["files_modified"] > 0:
        files_modified = cleanup_stats["files_modified"]
        chars_replaced = cleanup_stats["unicode_replaced"]
        print(
            log_message(
                f"Unicode cleanup completed: {files_modified} files modified, "
                f"{chars_replaced} characters replaced"
            )
        )
    elif cleanup_stats["files_processed"] > 0:
        print(log_message("Unicode cleanup completed: no Unicode characters found"))

    if cleanup_stats["errors"]:
        for error in cleanup_stats["errors"]:
            print(log_message(f"Cleanup error: {error}", "WARN"))


def main() -> bool:
    """Execute hook function - called by Claude Code after tool use."""
    try:
        # Parse hook input from stdin or environment
        hook_input = _parse_hook_input()

        # Extract tool information
        tool_name = hook_input.get("tool_name", os.environ.get("CLAUDE_TOOL_NAME", ""))
        tool_input = hook_input.get("tool_input", {})

        # Guard clause: Only process file modification tools
        if not _should_process_tool(tool_name):
            return True  # Not a file modification tool, exit silently

        print(log_message(f"Post-tool Unicode cleanup triggered by {tool_name}"))

        # Extract file paths that were modified
        modified_files = extract_file_paths_from_tool_result(tool_name, tool_input)

        # Guard clause: No files to process
        if not modified_files:
            print(log_message("No files to clean up"))
            return True

        print(log_message(f"Cleaning Unicode in {len(modified_files)} file(s)"))

        # Run Unicode cleanup and report results
        cleanup_stats = cleanup_unicode_in_files(modified_files)
        _report_cleanup_results(cleanup_stats)

        return True

    except Exception as e:
        print(log_message(f"Unicode cleanup hook failed: {e}", "ERROR"))
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
