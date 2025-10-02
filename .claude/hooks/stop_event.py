#!/usr/bin/env python3
"""Simple Stop hook wrapper."""

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

        # Handle the hook
        result = orchestrator.handle_stop()

        if result["success"]:
            print("Stop hook completed successfully")
        else:
            print(f"Stop hook failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"Stop hook error: {e}")


if __name__ == "__main__":
    main()
