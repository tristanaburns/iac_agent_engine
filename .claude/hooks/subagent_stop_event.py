#!/usr/bin/env python3
"""Simple SubagentStop hook wrapper."""

import sys
from pathlib import Path

from orchestrator import Orchestrator

# Add hooks directory to path
hooks_dir = Path(__file__).parent
sys.path.insert(0, str(hooks_dir))


def main():
    """Main hook entry point."""
    try:
        orchestrator = Orchestrator()

        # Extract agent info from environment or args
        agent_name = sys.argv[1] if len(sys.argv) > 1 else None

        # Handle the hook
        result = orchestrator.handle_subagent_stop(agent_name)

        if result["success"]:
            print("SubagentStop completed successfully")
        else:
            print(f"SubagentStop failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"SubagentStop hook error: {e}")


if __name__ == "__main__":
    main()
