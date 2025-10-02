#!/usr/bin/env python3
"""Simple PostToolUse hook wrapper."""

import sys
from pathlib import Path

# Orchestrator will be imported inside main() after path setup


def main() -> None:
    """Execute PostToolUse hook and delegate to orchestrator."""
    try:
        # Add hooks directory to path and import orchestrator
        hooks_dir = Path(__file__).parent
        sys.path.insert(0, str(hooks_dir))
        from orchestrator import Orchestrator  # type: ignore[import]

        orchestrator = Orchestrator()

        # Extract tool info from environment or args
        tool_name = sys.argv[1] if len(sys.argv) > 1 else "Edit"
        tool_result = sys.argv[2] if len(sys.argv) > 2 else None

        # Handle the hook
        result = orchestrator.handle_post_tool_use(tool_name, tool_result)

        if result["success"]:
            print("PostToolUse completed successfully")
        else:
            print(f"PostToolUse failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"PostToolUse hook error: {e}")


if __name__ == "__main__":
    main()
