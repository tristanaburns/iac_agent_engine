#!/usr/bin/env python3
"""Simple wrapper hook for Stop events (session end).

This hook follows SOLID principles by having a single responsibility:
Receive Stop events and delegate to the main orchestrator.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict


def main() -> int:
    """Handle Stop hook event and delegate to main orchestrator.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Add parent directory to path for imports
    hooks_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(hooks_dir))

    try:
        # Import orchestrator with proper path setup
        from orchestrators.main_orchestrator import MainOrchestrator

        # Additional context from environment
        context: Dict[str, Any] = {
            "project_dir": os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
            "session_id": os.environ.get("CLAUDE_SESSION_ID", ""),
            "timestamp": os.environ.get("CLAUDE_TIMESTAMP", ""),
            "session_duration": os.environ.get("CLAUDE_SESSION_DURATION", ""),
        }

        # Initialize orchestrator and handle event
        orchestrator = MainOrchestrator()
        result: Dict[str, Any] = orchestrator.handle_stop(context=context)

        # Return success/failure
        return 0 if result.get("success", False) else 1

    except Exception as e:
        print(f"[ERROR] Stop hook failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
