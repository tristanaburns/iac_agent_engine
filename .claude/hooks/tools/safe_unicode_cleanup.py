#!/usr/bin/env python3
"""
Safe Unicode/Emoji Cleanup Script.

=================================

This script uses the UnicodeManager to safely clean up emoji and Unicode characters
from the codebase while preserving Python formatting and excluding pip directories.

Author: System
Version: 1.0.0
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# Import local unicode manager
try:
    from .unicode_manager import UnicodeManager
except ImportError as e:
    print(f"Error importing UnicodeManager: {e}")
    print("Please ensure the unicode_manager.py module is in the same directory")
    sys.exit(1)


def _print_header() -> None:
    """Print the header for the cleanup script."""
    print("=" * 60)
    print("SAFE UNICODE/EMOJI CLEANUP")
    print("=" * 60)
    print()


def _setup_unicode_manager() -> UnicodeManager:
    """Set up and return the Unicode Manager instance."""
    unicode_manager = UnicodeManager()
    print("Using default Unicode Manager configuration")
    print()
    return unicode_manager


def _get_target_directories(project_root: Path) -> List[Path]:
    """Get and validate target directories for processing."""
    target_dirs: List[Path] = [
        project_root / ".claude" / "hooks",
        project_root / "llm-gateway" / "src",
        project_root / "langflow-plugin-framework" / "src",
        project_root / "project",
    ]

    print("Target directories:")
    for target_dir in target_dirs:
        if target_dir.exists():
            print(f" [OK] {target_dir}")
        else:
            print(f" [FAIL] {target_dir} (not found)")
    print()

    return target_dirs


def _process_directory(
    target_dir: Path,
    unicode_manager: UnicodeManager,
    project_root: Path,
    stats: Dict[str, int],
) -> None:
    """Process a single directory for Unicode cleanup."""
    if not target_dir.exists():
        return

    print(f"Processing directory: {target_dir}")

    for file_path in target_dir.rglob("*"):
        if file_path.is_file():
            result = unicode_manager.process_file(file_path)

            if result["processed"]:
                stats["processed"] += 1
                if result["modified"]:
                    stats["modified"] += 1
                    stats["unicode_replaced"] += result["unicode_replaced"]
                    replacements = result["unicode_replaced"]
                    rel_path = file_path.relative_to(project_root)
                    print(
                        f" [OK] Modified: {rel_path} " f"({replacements} replacements)"
                    )
            elif result["error"] and "excluded" not in result["error"]:
                rel_path = file_path.relative_to(project_root)
                error_msg = result["error"]
                print(f"  Skipped: {rel_path} " f"({error_msg})")


def _print_summary(stats: Dict[str, int], unicode_manager: UnicodeManager) -> None:
    """Print the cleanup summary and statistics."""
    print()
    print("=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"Files processed: {stats['processed']}")
    print(f"Files modified: {stats['modified']}")
    print(f"Unicode characters replaced: {stats['unicode_replaced']}")

    # Get detailed stats
    detailed_stats: Dict[str, Any] = unicode_manager.get_stats()
    print()
    print("Detailed Statistics:")
    for key, value in detailed_stats.items():
        print(f" {key.replace('_', ' ').title()}: {value}")

    print()
    if stats["modified"] > 0:
        print("[OK] Cleanup completed successfully!")
        print("[OK] Backups were created for modified files")
        print("[OK] Python formatting has been preserved")
    else:
        print("[OK] No Unicode/emoji characters found - codebase is clean!")


def main() -> bool:
    """Execute the Unicode Manager with safe settings."""
    _print_header()

    # Get project root
    project_root = Path(__file__).parent.parent.parent

    # Setup Unicode Manager
    unicode_manager = _setup_unicode_manager()

    # Get target directories
    target_dirs = _get_target_directories(project_root)

    # Initialize processing statistics
    stats = {"processed": 0, "modified": 0, "unicode_replaced": 0}

    # Process each directory
    for target_dir in target_dirs:
        _process_directory(target_dir, unicode_manager, project_root, stats)

    # Print summary
    _print_summary(stats, unicode_manager)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
