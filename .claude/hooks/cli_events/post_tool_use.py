#!/usr/bin/env python3
"""Wrapper hook for PostToolUse events.

This hook follows SOLID principles by having a single responsibility:
Receive PostToolUse events and delegate to the main orchestrator.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def main() -> int:
    """Handle PostToolUse hook event and delegate to main orchestrator.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Add parent directory to path for imports
    hooks_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(hooks_dir))

    try:
        # Import orchestrator with proper path setup
        from orchestrators.main_orchestrator import MainOrchestrator

        # Get tool information from environment
        tool_name: str = os.environ.get("CLAUDE_TOOL_NAME", "unknown")
        tool_result: str = os.environ.get("CLAUDE_TOOL_RESULT", "")

        # Additional context from environment
        context: Dict[str, Any] = {
            "project_dir": os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
            "session_id": os.environ.get("CLAUDE_SESSION_ID", ""),
            "timestamp": os.environ.get("CLAUDE_TIMESTAMP", ""),
        }

        # Check for file paths in environment
        file_paths_env: Optional[str] = os.environ.get("CLAUDE_FILE_PATHS")
        if file_paths_env:
            context["file_paths"] = file_paths_env.split(",")

        # Initialize orchestrator and handle event
        orchestrator = MainOrchestrator()
        result: Dict[str, Any] = orchestrator.handle_post_tool_use(
            tool_name=tool_name, tool_result=tool_result, context=context
        )

        # Return success/failure
        return 0 if result.get("success", False) else 1

    except Exception as e:
        print(f"[ERROR] PostToolUse hook failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
