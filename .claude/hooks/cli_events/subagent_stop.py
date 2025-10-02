#!/usr/bin/env python3
"""Simple wrapper hook for SubagentStop events.

This hook follows SOLID principles by having a single responsibility:
Receive SubagentStop events and delegate to the main orchestrator.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict


def main() -> int:
    """Handle SubagentStop hook event and delegate to main orchestrator.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Add parent directory to path for imports
    hooks_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(hooks_dir))

    try:
        # Import orchestrator with proper path setup
        from orchestrators.main_orchestrator import MainOrchestrator

        # Get agent information from environment
        agent_name: str = os.environ.get("CLAUDE_AGENT_NAME", "unknown")

        # Additional context from environment
        context: Dict[str, Any] = {
            "project_dir": os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
            "session_id": os.environ.get("CLAUDE_SESSION_ID", ""),
            "timestamp": os.environ.get("CLAUDE_TIMESTAMP", ""),
            "agent_result": os.environ.get("CLAUDE_AGENT_RESULT", ""),
        }

        # Initialize orchestrator and handle event
        orchestrator = MainOrchestrator()
        result: Dict[str, Any] = orchestrator.handle_subagent_stop(
            agent_name=agent_name, context=context
        )

        # Return success/failure
        return 0 if result.get("success", False) else 1

    except Exception as e:
        print(f"[ERROR] SubagentStop hook failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
